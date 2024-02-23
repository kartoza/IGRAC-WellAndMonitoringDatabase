"""Harvester of using hubeau."""

import json

import requests
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester, HarvesterAttribute
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    Well, MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class Hubeau(BaseHarvester):
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

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND)
        super(Hubeau, self).__init__(harvester, replace, original_id)

    def _process(self):
        """Processing the data."""
        self.codes = None
        try:
            self.codes = json.loads(self.attributes['codes'])
        except Exception:
            pass
        self.re_fetch = self.attributes.get('re-fetch', False)
        self.re_fetch_codes_done = json.loads(
            self.attributes.get(self.re_fetch_codes_done_key, '[]')
        )

        self.countries = []
        # Process the stations
        self._process_stations(
            f'{self.domain}/stations?'
            'format=json&nb_mesures_piezo_min=2&size=100'
        )

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)
        self._done('Done')

    def check_prefetch_wells(self, well):
        """Get prefetch wells is needed or not"""
        if self.re_fetch:
            original_id = well.original_id
            if original_id not in self.re_fetch_codes_done:
                self._update(f'{original_id} - Deleting measurements')
                well.welllevelmeasurement_set.all().delete()
                self.re_fetch_codes_done.append(original_id)
                attr, _ = HarvesterAttribute.objects.get_or_create(
                    harvester=self.harvester,
                    name=self.re_fetch_codes_done_key
                )
                attr.value = json.dumps(self.re_fetch_codes_done)
                attr.save()

    def _measurement_url(self, params_dict: dict):
        """Construct url for measurement"""
        measurement_params = {
            'size': 500,
            'fields': 'date_mesure,profondeur_nappe'
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
            for station in stations:
                original_id = station[self.original_id_key]
                if self.codes and original_id not in self.codes:
                    continue

                self.updated = False
                geometry = station['geometry']
                if not geometry or not geometry['coordinates']:
                    continue
                latitude = geometry['coordinates'][1]
                longitude = geometry['coordinates'][0]

                last_date = None
                well = self.get_well(original_id, latitude, longitude)
                # We just filter by latest one
                if well:
                    # Remove all measurements if re-fetch
                    self.check_prefetch_wells(well)
                    last = well.welllevelmeasurement_set.first()
                    if last:
                        last_date = last.time.strftime("%Y-%m-%d")

                # Process measurement
                try:
                    # -----------------------
                    # Process after
                    params = {
                        'code_bss': original_id,
                        'sort': 'asc'

                    }
                    if last_date:
                        params['date_debut_mesure'] = last_date
                    self._process_measurements(
                        self._measurement_url(params), station, None
                    )

                    # -----------------------
                    # Generate cache
                    well = self.get_well(original_id, latitude, longitude)
                    if well and self.updated:
                        self.post_processing_well(
                            well, generate_country_cache=False
                        )
                        self.countries.append(well.country.code)
                except (
                        Well.DoesNotExist, requests.exceptions.ConnectionError
                ):
                    pass
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
            original_id = station[self.original_id_key]
            site_name = station['nom_commune']
            altitude = float(station['altitude_station'])
            latitude = station['geometry']['coordinates'][1]
            longitude = station['geometry']['coordinates'][0]

            data = response.json()
            measurements = data['data']
            self._update(f'{original_id} - {len(measurements)} - {url}')
            if measurements:
                # Save well
                if not harvester_well_data:
                    well, harvester_well_data = self._save_well(
                        original_id=original_id,
                        name=site_name,
                        latitude=latitude,
                        longitude=longitude,
                        ground_surface_elevation_masl=altitude
                    )

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
                        measurement['profondeur_nappe'],
                        self.unit_m
                    )
                    self.updated = True
                if data['next']:
                    self._process_measurements(
                        data['next'], station, harvester_well_data
                    )
        else:
            pass
