"""Harvester of ehyd file that they pushe to database."""

import csv
import os
import re
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

last_file_key = 'last-file'
check_old_data_done_key = 'check-old-data'


class FileBase(BaseHarvester):
    """Harvester for file sftp that they push to it."""
    updated = False
    folder = settings.SFTP_FOLDER

    def __init__(
            self, harvester: Harvester,
            replace: bool = False,
            original_id: str = None
    ):
        # Instance-level state so nothing leaks across runs.
        self.wells_by_original_id = {}
        # Updated wells keyed by id, so each is post-processed once.
        self.wells = {}
        # well id -> {(year, month): set of existing times}
        self.existing_times = {}
        self.countries = []
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        super(FileBase, self).__init__(harvester, replace, original_id)

    def process_folder(self, folder, old_data=False):
        """process folder."""
        if not os.path.exists(folder):
            return
        if old_data and self.check_old_data_done:
            return
        files = os.listdir(folder)
        files.sort()
        last_file = self.last_file
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ['.asc', '.dat']:
                try:
                    if not old_data:
                        datetime.strptime(name, '%Y%m%d%H%M%S')
                    if not last_file or filename > last_file:
                        # Process it because of the file is new
                        last_file = filename
                        self.process_measurements(
                            os.path.join(folder, filename)
                        )
                        self.update_attribute(last_file_key, filename)
                except ValueError as e:
                    print(e)
                    pass
        if old_data:
            self.update_attribute(check_old_data_done_key, True)

    def _process(self):
        """Pass the process."""
        self.check_old_data_done = self.attributes.get(
            'check-old-data-done', False
        )
        self.last_file = self.attributes.get(last_file_key, None)

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
                well = self._save_well(
                    row['ID'],
                    row['name'],
                    longitude=point.coords[0],
                    latitude=point.coords[1],
                    ground_surface_elevation_masl=row[
                        'ground level (m above Adriatic Sea)'
                    ]
                )
                self.wells_by_original_id[row['ID']] = well
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

        self.process_folder(os.path.join(self.folder, 'old'), True)
        self.process_folder(self.folder)

        # Process cache
        for well in self.wells.values():
            self._update(f'Processing cache {well.original_id}')
            self.post_processing_well(well)

    @staticmethod
    def _month_key(time: datetime):
        """Return (year, month) key of a time."""
        return time.year, time.month

    @staticmethod
    def _month_range(time: datetime):
        """Return [start, end) of the month of a time, keeping its tz."""
        start = time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        return start, end

    def get_existing_times(self, well, time: datetime) -> set:
        """Return existing measurement times of a well in a month.

        Loaded from database once per (well, month) and cached, so
        overlapping files don't query the same month again.
        """
        months = self.existing_times.setdefault(well.id, {})
        key = self._month_key(time)
        if key not in months:
            start, end = self._month_range(time)
            months[key] = set(
                WellLevelMeasurement.objects.filter(
                    well=well,
                    parameter=self.parameter,
                    time__gte=start,
                    time__lt=end
                ).values_list('time', flat=True)
            )
        return months[key]

    def evict_existing_times(self, well, oldest_key):
        """Drop cached months of a well older than oldest_key.

        Files are processed in ascending order, so months before the
        earliest month in the current block won't be needed again.
        """
        months = self.existing_times.get(well.id, {})
        for key in [key for key in months if key < oldest_key]:
            del months[key]

    def process_measurement(self, data):
        """Process measurement."""
        try:
            _id = data['DBMS-Nummer']
        except KeyError:
            _id = data["Ort"]

        self._update(f'Saving measurement for well {_id}')
        try:
            well = self.wells_by_original_id[_id]
        except KeyError:
            print('Not found')
            return

        # Block without "Werte:" has no measurements
        measurements = data.get('measurements', [])
        if not measurements:
            return

        self.evict_existing_times(
            well, min(self._month_key(m['time']) for m in measurements)
        )

        # Skip times that already exist, including duplicates in the block
        new_measurements = []
        for measurement in measurements:
            existing = self.get_existing_times(well, measurement['time'])
            if measurement['time'] in existing:
                continue
            existing.add(measurement['time'])
            new_measurements.append(measurement)

        if not new_measurements:
            return

        quantities = Quantity.objects.bulk_create([
            Quantity(unit=self.unit_m, value=measurement['value'])
            for measurement in new_measurements
        ])
        objs = []
        for measurement, quantity in zip(new_measurements, quantities):
            obj = WellLevelMeasurement(
                well=well,
                parameter=self.parameter,
                time=measurement['time'],
                value=quantity,
                value_in_m=measurement['value']
            )
            # bulk_create skips pre_save, so set default value here.
            # Well counters are refreshed in post_processing_well.
            obj.set_default_value()
            objs.append(obj)
        WellLevelMeasurement.objects.bulk_create(objs)
        self.wells[well.id] = well

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
            if 'Werte:' in line:
                is_measurement = True
                data['measurements'] = []
                continue

            # ------------------------------------------------
            # If measurements
            # Save it to data['measurements']
            # ------------------------------------------------
            if is_measurement:
                try:
                    line = re.sub(' +', ' ', line)
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
                except (IndexError, ValueError):
                    pass
                continue

            # ------------------------------------------------
            # If not measurements
            # ------------------------------------------------
            row_data = line.split(':')
            try:
                data[row_data[0]] = row_data[1].replace(' ', '')
            except IndexError:
                pass
        self.process_measurement(data)
