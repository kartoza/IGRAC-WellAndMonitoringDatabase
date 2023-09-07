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
    MEASUREMENT_PARAMETER_AMSL, Well, WellLevelMeasurement
)


class EHYD(BaseHarvester):
    """
    Harvester for file sftp that they push to it
    """
    updated = False
    folder = settings.SFTP_FOLDER

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
        if not os.path.exists(self.folder):
            raise HarvestingError(
                f'Sftp folder not found or not setup. current: {self.folder}'
            )

        ori_coord = SpatialReference(31287)
        target_coord = SpatialReference(4326)
        trans = CoordTransform(ori_coord, target_coord)

        # Get csv file that contains wells data
        for (root, dirs, file) in os.walk(self.folder):
            for f in file:
                split_name = os.path.splitext(f)
                if split_name[1] == '.csv':
                    _file = open(
                        os.path.join(root, f), 'r',
                        encoding="utf8", errors='ignore'
                    )
                    reader = csv.DictReader(_file, delimiter=';')

                    for row in list(reader):
                        try:
                            x = row['X (Lambert cone right)']
                            y = row['Y (Lambert cone high)']
                            point = Point(float(y), float(x), srid=31287)
                            point.transform(trans)
                            date = parser.parse(
                                row['date of construction']
                            )

                            well, harvester_well_data = self._save_well(
                                row['ID'],
                                row['name'],
                                longitude=point.coords[1],
                                latitude=point.coords[0],
                                ground_surface_elevation_masl=row[
                                    'ground level (m above Adriatic Sea)'
                                ]
                            )
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

        # Get all files that found
        for (root, dirs, file) in os.walk(self.folder):
            for f in file:
                split_name = os.path.splitext(f)
                if split_name[1] == '.csv':
                    continue
                self._update(f'Check file {f}')
                _file = open(
                    os.path.join(root, f), 'r',
                    encoding="utf8", errors='ignore'
                )
                lines = _file.readlines()

                data = {}
                is_measurement = False
                for line in lines:
                    line = line.replace('\n', '')
                    # Parse data per measurement
                    # Start with BEGIN
                    if line == 'BEGIN':
                        try:
                            updated = False
                            # Save the data
                            x = data['X']
                            y = data['Y']
                            point = Point(float(y), float(x), srid=31287)
                            point.transform(trans)
                            self._update(f'Saving well {data["Ort"]}')
                            well, harvester_well_data = self._save_well(
                                data['Ort'],
                                '',
                                longitude=point.coords[1],
                                latitude=point.coords[0]
                            )
                            last_measurement = WellLevelMeasurement.objects.filter(
                                well=harvester_well_data.well,
                            ).order_by('-time').first()

                            for measurement in data['measurements']:
                                # Save measurements
                                if last_measurement and measurement[
                                    'time'] <= last_measurement.time:
                                    print('found')
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
                                self.post_processing_well(well)

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

                    # If measurements
                    if is_measurement:
                        columns = line.split(' ')
                        try:
                            measurement_time = datetime.strptime(
                                ' '.join([columns[0], columns[1]]),
                                '%d.%m.%Y %H:%M:%S'
                            ).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
                            measurement_value = float(columns[2])
                            data['measurements'].append({
                                'time': measurement_time,
                                'value': measurement_value
                            })

                            continue
                        except (Well.DoesNotExist, ValueError):
                            continue

                    row_data = line.split(': ')
                    try:
                        data[row_data[0]] = row_data[1]
                    except IndexError:
                        pass
        self._done('Done')
