# coding=utf-8
import requests
import re
import os
import json
import time
import calendar
import csv
from datetime import datetime
from shutil import copyfile
from openpyxl import load_workbook
from geopy.geocoders import Nominatim
from django.core.management.base import BaseCommand

CODE = 'code'
NAME = 'name'
GEOMETRY = 'geometry'
COORDINATES = 'coordinates'
LAT = 'lat'
LON = 'lon'
STATION_TYPE = 'station_type'
WELL_TEMPLATE_FILE = 'wells.xlsx'
WELL_MONITORING_FILE = 'monitoring_data.xlsx'
STATUS = 'status'
SURFACE_LEVEL = 'surface_level'
TIME_SERIES = 'timeseries'
FILTERS = 'filters'

# -- MONITORING
PARAMETER_GWmBGS = 'Water depth [from the ground surface]'
PARAMETER_GWmMSL = 'Water level elevation a.m.s.l.'
PARAMETER = {
    'GWmBGS': PARAMETER_GWmBGS,
    'GWmMSL': PARAMETER_GWmMSL
}

COUNTRIES_CODE_FILE = 'countries_codes_and_coordinates.csv'

DJANGO_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))


class Command(BaseCommand):

    ggmn_station_url = 'https://ggmn.lizard.net/api/v3/groundwaterstations/'
    ggmn_timeseries_url = 'https://ggmn.lizard.net/api/v3/timeseries/'
    well_ids = []
    well_data = {}
    countries_code = {}
    locator = Nominatim(user_agent='geocoder')
    max_page = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '-m',
            '--max_page',
            dest='max_page',
            default=0,
            help='Max pages to fetch, default is fetch all')

    def get_current_timestamp(self):
        """
        Return current timestamp
        """
        gmt = time.gmtime()
        return calendar.timegm(gmt)

    def read_countries_code(self):
        """
        Read data from countries code csv,
        then store it as a dictionary
        """
        csv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            COUNTRIES_CODE_FILE
        )
        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                line_count += 1
                if line_count == 1:
                    continue
                self.countries_code[
                    row[1].strip().replace('"', '')
                ] = row[2].strip().replace('"', '')


    def fetch_wells(self, well_template_output_path, page=1):
        """
        Fetch wells from api
        """
        if self.max_page:
            if page > self.max_page:
                return

        print('#- Processing page {}'.format(page))
        well_url = '{base_url}?page={page}'.format(
            base_url=self.ggmn_station_url,
            page=page
        )
        print(well_url)
        response = requests.get(well_url)
        ground_stations = response.json()

        wb = load_workbook(well_template_output_path)
        ws = wb.worksheets[0]

        for ground_station in ground_stations['results']:
            if ground_station[CODE] in self.well_ids:
                continue
            self.well_ids.append(ground_station[CODE])
            print('#-- Processing well {}'.format(ground_station[CODE]))
            lat = ground_station[GEOMETRY][COORDINATES][1]
            lon = ground_station[GEOMETRY][COORDINATES][0]
            location = self.locator.reverse(
                '{lat},{lon}'.format(
                    lat=lat,
                    lon=lon
                )
            )

            # Store well data for fetching monitoring data
            self.well_data[ground_station[CODE]] = []
            if FILTERS in ground_station:
                filters = ground_station[FILTERS]
                if len(filters) > 0:
                    _filter = filters[0]
                    if TIME_SERIES in _filter:
                        for time_series_data in _filter[TIME_SERIES]:
                            self.well_data[ground_station[CODE]].append({
                                time_series_data['name']:
                                    time_series_data['uuid']
                            })

            row_data = [
                ground_station[CODE], # ID
                ground_station[NAME], # NAME
                ground_station[STATUS].capitalize(), # Status
                '', # Feature Type
                '', # Purpose
                lat, # Lat
                lon, # Lon
                ground_station[SURFACE_LEVEL], # Ground surface elevation value
                'm', # Ground surface elevation unit
                '','', # Elevation of the top of the casing ( unknown )
                self.countries_code[
                    location.raw['address']['country_code'].upper()],
                '', # Address
                '' # Description
            ]
            ws.append(row_data)
        wb.save(well_template_output_path)
        if 'next' in ground_stations:
            next_url = ground_stations['next']
            next_page = int(re.findall(r'\d+', next_url)[-1])
            if self.max_page:
                if next_page <= self.max_page:
                    self.fetch_wells(well_template_output_path, next_page)
            else:
                self.fetch_wells(well_template_output_path, next_page)

    def fetch_monitoring_data(self, template_output_path, ):
        """
        Fetch monitoring data for wells
        """
        today_timestamp = int(time.mktime(datetime.today().timetuple())*1000)

        if not self.well_data:
            return

        wb = load_workbook(template_output_path)
        ws = wb.worksheets[0]

        # self.well_data e.g. {'B10H0082':
        # [{"GWmMSL": "167761f9-7691-44fa-a11e-addf331c3ff8"},
        # {"GWmBGS": "258f8f51-6c97-4829-ade3-b1ac4642ef72"}],..}
        for well_code in self.well_data:
            # well_code => "B10H0082"
            # well_data => [
            # {"GWmMSL": "167761f9-7691-44fa-a11e-addf331c3ff8"},
            # {"GWmBGS": "258f8f51-6c97-4829-ade3-b1ac4642ef72"}]
            well_data = self.well_data[well_code]

            # time_series => {"GWmMSL": "167761f9-7691-44fa-a11e-addf331c3ff8"}
            for time_series in well_data:
                for time_series_name in time_series:
                    # uuid => "167761f9-7691-44fa-a11e-addf331c3ff8"
                    # time_series_name => "GWmMSL"
                    uuid = time_series[time_series_name]
                    print('#-- Processing {name} uuid {uuid}'.format(
                        name=time_series_name,
                        uuid=uuid))
                    monitoring_url = (
                        '{base_url}?min_points={min_points}&start={start}'
                        '&end={end}'
                        '&uuid={uuid}'
                    ).format(
                        base_url=self.ggmn_timeseries_url,
                        min_points=0,
                        start=0,
                        end=today_timestamp,
                        uuid=uuid
                    )
                    print(monitoring_url)
                    response = requests.get(monitoring_url)
                    monitoring_data = response.json()

                    results = monitoring_data['results']
                    for result in results:
                        events = result['events']
                        for event in events:
                            timestamp = int(event['timestamp']/1000)
                            date_object = datetime.fromtimestamp(timestamp)
                            row_data = [
                                well_code,  # ID
                                date_object.strftime('%Y-%m-%d %H:%M'), # Date and time
                                PARAMETER[time_series_name], # Parameter
                                event['value'],  # Value
                                'm',  # Unit
                                '',  # Method
                            ]
                            ws.append(row_data)

        wb.save(template_output_path)


    def handle(self, *args, **options):
        """Implementation for command.
        :param args:  Not used
        :param options: Not used

        """
        self.read_countries_code()
        self.max_page = int(options.get('max_page'))

        print('# Fetching Wells ')
        well_template_path =  os.path.join(
            DJANGO_ROOT,
            'fixtures', 'download_template',
            WELL_TEMPLATE_FILE
        )
        well_template_output_name = '{file}_{time}.xlsx'.format(
            file='WELL',
            time=self.get_current_timestamp()
        )
        well_template_output_path = os.path.join(
            DJANGO_ROOT,
            well_template_output_name
        )
        copyfile(
            well_template_path,
            well_template_output_path
        )

        self.fetch_wells(well_template_output_path)

        print('# Fetching Monitoring data')
        well_monitoring_template_path = os.path.join(
            DJANGO_ROOT,
            'fixtures', 'download_template',
            WELL_MONITORING_FILE
        )
        well_monitoring_template_output_name = '{file}_{time}.xlsx'.format(
            file='WELL_MONITORING',
            time=self.get_current_timestamp()
        )
        well_monitoring_template_output_path = os.path.join(
            DJANGO_ROOT,
            well_monitoring_template_output_name
        )
        copyfile(
            well_monitoring_template_path,
            well_monitoring_template_output_path
        )
        self.fetch_monitoring_data(well_monitoring_template_output_path)
