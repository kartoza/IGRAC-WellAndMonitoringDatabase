"""Harvester of using hubeau."""

import json

import requests
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    Well, MEASUREMENT_PARAMETER_AMSL, WellLevelMeasurement
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class HubeauWaterLevel(BaseHarvester):
    """
    Harvester for https://hubeau.eaufrance.fr/page/api-piezometrie

    attributes :
    - codes : List of code_bss
              Limit the codes that will be fetched.
    - re-fetch : boolean
              Telling the harvester to try re fetching all measurement.
    """
    domain = 'https://hubeau.eaufrance.fr/api/v1/niveaux_nappes'
    original_id_key = 'code_bss'
    updated = False
    re_fetch_codes_done_key = 're-fetch-codes-done'
    last_code_key = 'last-code'
    stations_url_key = 'stations-url'
    current_idx = 0
    proceed = False

    # Filter the index by using - separator
    index_filter = 'index-filter'

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        super(HubeauWaterLevel, self).__init__(harvester, replace, original_id)

    def _process(self):
        """Processing the data."""
        self.codes = None
        try:
            self.codes = json.loads(self.attributes['codes'])
        except Exception:
            pass

        self.indexes = None
        try:
            indexes = self.attributes['index-filter'].split('-')
            self.indexes = [
                int(indexes[0]), int(indexes[1])
            ]
        except Exception:
            pass

        if self.indexes:
            if self.indexes[0] > self.indexes[0]:
                raise Exception(
                    'First index on index-filter is greater than last index'
                )

        # Check last code
        self.last_code = self.attributes.get(self.last_code_key, None)
        if not self.last_code:
            self.proceed = True

        self.re_fetch = self.attributes.get('re-fetch', False)
        self.re_fetch_codes_done = json.loads(
            self.attributes.get(self.re_fetch_codes_done_key, '[]')
        )

        self.countries = []
        # Process the stations
        station_url = self.attributes.get(
            self.stations_url_key, (
                f'{self.domain}/stations?'
                f'format=json&nb_mesures_piezo_min=2&size=2000'
            )
        )
        self._process_stations(station_url)
        self.delete_attribute(self.last_code_key)

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def check_prefetch_wells(self, well, original_id):
        """Get prefetch wells is needed or not"""
        if self.re_fetch:
            if well:
                original_id = well.original_id
                if original_id not in self.re_fetch_codes_done:
                    self._update(
                        f'[{self.current_idx}/{self.count}] '
                        f'{original_id} - Deleting measurements'
                    )
                    well.welllevelmeasurement_set.all().delete()

            # Save this to re fetch codes done
            if original_id not in self.re_fetch_codes_done:
                self.re_fetch_codes_done.append(original_id)
                self.update_attribute(
                    self.re_fetch_codes_done_key,
                    json.dumps(self.re_fetch_codes_done)
                )

    def _measurement_url(self, params_dict: dict):
        """Construct url for measurement"""
        measurement_params = {
            'size': 500,
            'fields': 'date_mesure,niveau_nappe_eau'
        }
        measurement_params.update(params_dict)

        params = []
        for key, value in measurement_params.items():
            params.append(f'{key}={value}')
        return f'{self.domain}/chroniques?{"&".join(params)}'

    def _process_stations(self, url: str):
        """Process the stations from the url.

        After it is finished, do the next url.
        """
        print(f'Process {url}')
        response = requests.get(url)
        if response.status_code in [200, 206]:
            data = response.json()
            stations = data['data']
            self.count = data['count']

            for station in stations:
                self.current_idx += 1
                if self.indexes:
                    if (
                            self.current_idx < self.indexes[0] or
                            self.current_idx > self.indexes[1]
                    ):
                        continue

                original_id = station[self.original_id_key]
                self._update(
                    f'[{self.current_idx}/{self.count}] '
                    f'{original_id} - Checking'
                )

                # Check last code, if there, skip if not found yet
                if self.last_code:
                    if original_id == self.last_code:
                        self.proceed = True

                if self.codes and original_id not in self.codes:
                    continue

                if not self.proceed:
                    continue

                self.updated = False

                # Save the well
                geometry = station['geometry']
                if not geometry or not geometry['coordinates']:
                    continue

                latitude = geometry['coordinates'][1]
                longitude = geometry['coordinates'][0]
                original_id = station[self.original_id_key]
                site_name = station['nom_commune']
                altitude = float(station['altitude_station'])

                # Process measurement
                try:
                    # Save well
                    well, harvester_well_data = self._save_well(
                        original_id=original_id,
                        name=site_name,
                        latitude=latitude,
                        longitude=longitude,
                        ground_surface_elevation_masl=altitude,
                        reassign_organisation=True
                    )

                    # Prefetch well
                    self.check_prefetch_wells(well, original_id)

                    # We just filter by latest one
                    last_date = None
                    first_date = None
                    if well:
                        last = well.welllevelmeasurement_set.first()
                        if last:
                            last_date = last.time.strftime("%Y-%m-%d")
                        first = well.welllevelmeasurement_set.last()
                        if first:
                            first_date = first.time.strftime("%Y-%m-%d")

                    # -----------------------
                    # Process after
                    params = {
                        'code_bss': original_id,
                        'sort': 'asc'
                    }

                    if last_date:
                        params['date_debut_mesure'] = last_date
                    self._process_measurements(
                        self._measurement_url(params), station,
                        harvester_well_data
                    )

                    if first_date:
                        params = {
                            'code_bss': original_id, 'sort': 'desc',
                            'date_fin_mesure': first_date
                        }

                        self._process_measurements(
                            self._measurement_url(params), station,
                            harvester_well_data
                        )

                    # -----------------------
                    # Generate cache
                    if well and self.updated:
                        self.post_processing_well(
                            well, generate_country_cache=False
                        )
                        if well.country:
                            self.countries.append(well.country.code)
                except (
                        Well.DoesNotExist, requests.exceptions.ConnectionError
                ):
                    pass

                self.update_attribute(
                    self.last_code_key, original_id
                )
            if data['next']:
                self._process_stations(data['next'])
        else:
            pass

    def _process_measurements(
            self, url: str, station: dict, harvester_well_data=None
    ):
        """Process the measurements from the url.

        After it is finished, do the next url.
        """
        response = requests.get(url)
        if response.status_code in [200, 206]:
            data = response.json()
            measurements = data['data']
            self._update(
                f'[{self.current_idx}/{self.count}] '
                f'{harvester_well_data.well.original_id} - {len(measurements)} - {url}'
            )
            if measurements:
                # Save measurements
                for measurement in measurements:
                    time = parse(measurement['date_mesure'])
                    defaults = {
                        'parameter': self.parameter
                    }
                    self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        measurement['niveau_nappe_eau'],
                        self.unit_m
                    )
                    self.updated = True
                if data['next']:
                    self._process_measurements(
                        data['next'], station, harvester_well_data
                    )
        else:
            pass
