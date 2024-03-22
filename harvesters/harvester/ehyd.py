"""Harvester of ehyd file that they pushe to database."""

import csv
import os
from datetime import datetime

import pytz
from dateutil import parser
from django.conf import settings
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester, HarvestingError
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.drilling import Drilling
from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_AMSL, WellLevelMeasurement
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)

last_file_key = 'last-file'


class EHYD(BaseHarvester):
    """
    Harvester for file sftp that they push to it
    """
    updated = False
    folder = settings.SFTP_FOLDER
    wells_by_original_id = {}
    wells = []
    countries = []

    def __init__(
            self, harvester: Harvester,
            replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        super(EHYD, self).__init__(harvester, replace, original_id)

    def _process(self):
        """Pass the process."""
        try:
            self.last_file = self.attributes.get(last_file_key, None)
        except Exception:
            pass

        if not os.path.exists(self.folder):
            raise HarvestingError(
                'Sftp folder not found or not setup correctly. '
                f'Current: {self.folder}'
            )

        ori_coord = SpatialReference(31287)
        target_coord = SpatialReference(4326)
        self.trans = CoordTransform(ori_coord, target_coord)

        # Check the wells
        well_file = os.path.join(self.folder, 'base data.csv')
        if not os.path.exists(well_file):
            raise HarvestingError(
                '"base data.csv" is not exist. '
                'Please put it to provide list of wells.'
            )

        # Get csv file that contains wells data
        _file = open(
            well_file, 'r', encoding="utf8", errors='ignore'
        )
        reader = csv.DictReader(_file, delimiter=';')

        for row in list(reader):
            try:
                x = row['X (Lambert cone right)']
                y = row['Y (Lambert cone high)']
                point = Point(float(x), float(y), srid=31287)
                point.transform(self.trans)
                date = parser.parse(
                    row['date of construction']
                )
                self._update(f'Checking well {row["ID"]}')
                well, harvester_well_data = self._save_well(
                    row['ID'],
                    row['name'],
                    longitude=point.coords[0],
                    latitude=point.coords[1],
                    ground_surface_elevation_masl=row[
                        'ground level (m above Adriatic Sea)'
                    ]
                )
                last_measurement = WellLevelMeasurement.objects.filter(
                    well=well,
                ).order_by('-time').first()
                self.wells_by_original_id[row['ID']] = {
                    'harvester_well_data': harvester_well_data,
                    'last_measurement': last_measurement
                }
                if well.drilling:
                    drilling = well.drilling
                else:
                    drilling = Drilling.objects.create(
                        year_of_drilling=date.year
                    )
                well.drilling = drilling
                well.save()
            except (KeyError, ValueError):
                continue

        files = os.listdir(self.folder)
        files.sort()
        last_file = self.last_file
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.asc':
                try:
                    datetime.strptime(name, '%Y%m%d%H%M%S')
                    if not last_file or filename > last_file:
                        # Process it because of the file is new
                        last_file = filename
                        self.process_measurements(
                            os.path.join(self.folder, filename)
                        )
                        self.update_attribute(last_file_key, filename)
                except ValueError as e:
                    pass

        # Process cache
        for well in self.wells:
            self._update(f'Processing cache {well.original_id}')
            self.post_processing_well(well, generate_country_cache=False)

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_measurement(self, data):
        """Process measurement."""
        updated = False
        # Save the data
        x = data['X']
        y = data['Y']
        point = Point(float(y), float(x), srid=31287)
        point.transform(self.trans)
        self._update(f'Saving measurement for well {data["Ort"]}')
        well_metadata = self.wells_by_original_id[data['Ort']]
        harvester_well_data = well_metadata['harvester_well_data']
        last_measurement = well_metadata['last_measurement']
        well = harvester_well_data.well

        for measurement in data['measurements']:
            # Save measurements
            if last_measurement and \
                    measurement['time'] <= last_measurement.time:
                continue
            defaults = {
                'parameter': self.parameter,
                'value_in_m': measurement['value']
            }
            obj = self._save_measurement(
                WellLevelMeasurement,
                measurement['time'],
                defaults,
                harvester_well_data
            )
            if not obj.value:
                obj.value = Quantity.objects.create(
                    unit=self.unit_m,
                    value=measurement['value']
                )
                obj.save()
            updated = True
        if updated:
            self.wells.append(well)
            self.countries.append(well.country.code)

    def process_measurements(self, path):
        """Process measurements."""
        self._update(f'Check file {path}')
        _file = open(path, 'r', encoding="utf8", errors='ignore')
        lines = _file.readlines()

        data = {}
        is_measurement = False
        for line in lines:
            line = line.replace('\n', '')
            # Parse data per measurement
            # Start with BEGIN
            if line == 'BEGIN':
                try:
                    self.process_measurement(data)
                except KeyError:
                    pass
                data = {}
                is_measurement = False
                continue

            # If it is measurements word
            if line == 'Werte: ':
                is_measurement = True
                data['measurements'] = []
                continue

            # ------------------------------------------------
            # If measurements
            # Save it to data['measurements']
            # ------------------------------------------------
            if is_measurement:
                try:
                    columns = line.split(' ')
                    measurement_time = datetime.strptime(
                        ' '.join([columns[0], columns[1]]),
                        '%d.%m.%Y %H:%M:%S'
                    ).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
                    measurement_value = float(columns[2])
                    data['measurements'].append({
                        'time': measurement_time,
                        'value': measurement_value
                    })
                except ValueError:
                    pass
                continue

            # ------------------------------------------------
            # If not measurements
            # ------------------------------------------------
            row_data = line.split(': ')
            try:
                data[row_data[0]] = row_data[1]
            except IndexError:
                pass
        self.process_measurement(data)
