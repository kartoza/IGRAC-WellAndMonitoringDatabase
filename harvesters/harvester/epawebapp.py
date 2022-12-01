"""Harvester of using Epawebapp."""
import csv
from datetime import datetime
from io import BytesIO, StringIO
from zipfile import ZipFile

import requests
from django.utils.timezone import make_aware

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit
from gwml2.models.management import Management
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement
)


class Epawebapp(BaseHarvester):
    """
    Harvester for https://epawebapp.epa.ie/
    """
    url = 'https://epawebapp.epa.ie/Hydronet/output/'
    updated = False

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND)
        super(Epawebapp, self).__init__(harvester, replace, original_id)

    def _process(self):
        """ Run the harvester """

        # Fetch layers list
        layers = self._request_api(self.url + 'internet/layers/index.json')
        layer_link = None
        for layer in layers['_links']:
            try:
                if layer['label'] == 'Groundwater':
                    layer_link = layer['href']
            except KeyError:
                pass

        # Fetch stations list
        stations = self._request_api(self.url + 'internet/stations/index.json')
        stations_in_dict = {}
        for station in stations['_links']:
            try:
                stations_in_dict[station['id']] = station
            except KeyError:
                pass

        if not layer_link:
            self._error('Link for groundwater does not found.')
        else:
            # Check for all stations
            stations = self._request_api(self.url + layer_link)
            count = len(stations)
            for idx, station in enumerate(stations):
                self.updated = False
                try:
                    print(f'Processing --- {idx}/{count}')
                    station_data = stations_in_dict[
                        station['metadata_station_id']]
                    self.fetch_measurement(None, station, station_data)

                    # Regenerate cache
                    well = self.get_well(
                        station['metadata_station_no'],
                        latitude=float(station['metadata_station_latitude']),
                        longitude=float(station['metadata_station_longitude'])
                    )
                    if well and self.updated:
                        self.post_processing_well(well)

                except (ValueError, KeyError):
                    pass
            self._done('Done')

    def fetch_measurement(self, harvester_well_data, station, station_data):
        """Fetch measurements."""
        # Measurements
        url_measurements = self.url + station_data[
            'href'] + '/GWL/complete_15min.zip'
        response = requests.get(url_measurements)
        if response.status_code == 200:
            zip_file = ZipFile(BytesIO(response.content))
            for file in zip_file.filelist:
                reader = csv.reader(
                    StringIO(zip_file.read(file.filename).decode()),
                    delimiter=";"
                )
                last_date_time = None
                is_data = False
                for row in reader:
                    if is_data and row[1]:
                        date_time = make_aware(
                            datetime.strptime(
                                row[0], '%Y-%m-%d %H:%M:%S')
                        )

                        # Just save per 6 hours
                        if not last_date_time or (
                                date_time - last_date_time
                        ).seconds / 3600 >= 6:
                            if not harvester_well_data:
                                # Save well
                                well, harvester_well_data = self._save_well(
                                    original_id=station['metadata_station_no'],
                                    name=station[
                                        'metadata_station_name'],
                                    description=station[
                                        'metadata_Web_Desc'],
                                    latitude=float(
                                        station['metadata_station_latitude']
                                    ),
                                    longitude=float(
                                        station['metadata_station_longitude']
                                    ),
                                    ground_surface_elevation_masl=station[
                                        'metadata_GWREF_DATUM']
                                )
                                if well.management:
                                    management = well.management
                                else:
                                    management = Management.objects.create(
                                        manager=station[
                                            'metadata_STATION_OWNER']
                                    )
                                well.management = management
                                well.save()
                                last_data = harvester_well_data.well.welllevelmeasurement_set.first()
                                if last_data:
                                    last_date_time = last_data.time

                            if last_date_time and date_time < last_date_time:
                                continue

                            defaults = {
                                'parameter': self.parameter
                            }
                            self._save_measurement(
                                WellLevelMeasurement,
                                date_time,
                                defaults,
                                harvester_well_data,
                                float(row[1]),
                                self.unit_m
                            )
                            last_date_time = date_time
                            self.updated = True
                    # If #Timestamp, the next is data
                    if row[0] == '#Timestamp':
                        is_data = True
