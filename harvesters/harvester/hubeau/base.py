"""Harvester of using hubeau."""

import json

import requests
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterParameterMap, HarvesterWellData
)
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter, TermMeasurementParameterGroup
)
from gwml2.models.well import (
    Well
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class HubeauHarvester(BaseHarvester):
    """Hubeau harvester."""

    original_id_key = 'code_bss'
    last_code_key = 'last-code'
    current_idx = 0
    proceed = False
    updated = False

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameters = HarvesterParameterMap.get_json(harvester)
        super(HubeauHarvester, self).__init__(
            harvester, replace, original_id
        )

    @property
    def station_url(self):
        """Return station url."""
        raise NotImplementedError

    @property
    def measurement_url(self):
        """Return measurement url."""
        raise NotImplementedError

    def _process(self):
        """Processing the data."""
        try:
            self.codes = json.loads(self.attributes['codes'])
        except Exception:
            self.codes = None

        # Check last code
        self.last_code = self.attributes.get(self.last_code_key, None)
        if not self.last_code:
            self.proceed = True

        self.countries = []

        # Process the stations
        self._process_stations(self.station_url)
        self.delete_attribute(self.last_code_key)

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def _measurement_params_update(
            self, params_dict: dict, parameter_key: str
    ):
        """Return measurement url."""
        raise NotImplementedError

    def _measurement_url(self, params_dict: dict, parameter_key: str):
        """Construct url for measurement"""
        measurement_params = {
            'size': 500,
            'fields': ','.join(self.measurement_fields)
        }
        measurement_params.update(params_dict)
        measurement_params = self._measurement_params_update(
            measurement_params, parameter_key
        )

        params = []
        for key, value in measurement_params.items():
            params.append(f'{key}={value}')
        return f'{self.measurement_url}?{"&".join(params)}'

    def _process_stations(self, url):
        """Process the stations from the url.

        After it is finished, do the next url.
        """
        print(f'Process : {url}')
        response = requests.get(url)
        if response.status_code in [200, 206]:
            data = response.json()
            stations = data['data']
            self.count = data['count']

            for station in stations:
                self.updated = False
                if not station['date_debut_mesure']:
                    continue

                self.current_idx += 1
                original_id = station[self.original_id_key]
                print(original_id)
                self._update(
                    f'[{self.current_idx}/{self.count}] '
                    f'{original_id} - Checking'
                )

                if self.codes and original_id not in self.codes:
                    continue

                # Check last code, if there, skip if not found yet
                if self.last_code:
                    if original_id == self.last_code:
                        self.proceed = True

                if not self.proceed:
                    continue

                # Process the station
                self.process_station(station)
                self.update_attribute(
                    self.last_code_key, original_id
                )
            if data['next']:
                self._process_stations(data['next'])
        else:
            pass

    def process_station(
            self,
            station
    ):
        """Process the station"""
        # -------------------------------------
        # Save the well
        # -------------------------------------
        geometry = station['geometry']
        if not geometry or not geometry['coordinates']:
            return

        latitude = geometry['coordinates'][1]
        longitude = geometry['coordinates'][0]
        original_id = station[self.original_id_key]
        site_name = station['nom_commune']

        # Process measurement
        try:
            # Save well
            try:
                altitude = float(station['altitude_station'])
                well, harvester_well_data = self._save_well(
                    original_id=original_id,
                    name=site_name,
                    latitude=latitude,
                    longitude=longitude,
                    ground_surface_elevation_masl=altitude,
                    reassign_organisation=True
                )
            except KeyError:
                well, harvester_well_data = self._save_well(
                    original_id=original_id,
                    name=site_name,
                    latitude=latitude,
                    longitude=longitude,
                    reassign_organisation=True
                )

            # Process measurements
            for parameter_key, _parameter in self.parameters.items():
                parameter = _parameter['parameter']
                unit = _parameter['unit']
                MeasurementModel = (
                    TermMeasurementParameterGroup.get_measurement_model(
                        parameter
                    )
                )
                # Check last measurements
                last_date = None
                first_date = None
                if well:
                    last = well.welllevelmeasurement_set.first()
                    if last:
                        last_date = last.time.strftime("%Y-%m-%d")
                    first = well.welllevelmeasurement_set.last()
                    if first:
                        first_date = first.time.strftime("%Y-%m-%d")

                # Measurement params
                # ------------------------------
                # Processing after first date or from first
                params = {
                    self.measurement_station_id_key: original_id,
                    'sort': 'asc'
                }
                if last_date:
                    params[self.measurement_date_debut_key] = last_date
                self._process_measurements(
                    self._measurement_url(params, parameter_key),
                    harvester_well_data,
                    MeasurementModel, parameter,
                    unit
                )

                # Process before first date
                if first_date:
                    params = {
                        self.measurement_station_id_key: original_id,
                        self.measurement_date_fin_key: first_date,
                        'sort': 'desc'
                    }
                    self._process_measurements(
                        self._measurement_url(params, parameter_key),
                        harvester_well_data,
                        MeasurementModel, parameter,
                        unit
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

        # Update last station code
        self.update_attribute(self.last_code_key, original_id)

    @property
    def measurement_fields(self) -> list[str]:
        """Measurement of fields to be returned."""
        raise NotImplementedError

    @property
    def measurement_date_debut_key(self):
        """Measurement of date debut key."""
        raise NotImplementedError

    @property
    def measurement_date_fin_key(self):
        """Measurement of date debut key."""
        raise NotImplementedError

    @property
    def measurement_station_id_key(self):
        """Measurement of station id key."""
        raise NotImplementedError

    @property
    def measurement_date_key(self):
        """Measurement of date key."""
        raise NotImplementedError

    @property
    def measurement_value_key(self):
        """Measurement of unit key."""
        raise NotImplementedError

    def _process_measurements(
            self, url: str, harvester_well_data: HarvesterWellData,
            MeasurementModel, parameter: TermMeasurementParameter,
            unit: Unit = None
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
                f'{harvester_well_data.well.original_id} - {parameter.name} - '
                f'{len(measurements)} - '
                f'{url}'
            )
            if measurements:
                # Save measurements
                for measurement in measurements:
                    time = parse(measurement[self.measurement_date_key])
                    defaults = {
                        'parameter': parameter
                    }
                    self._save_measurement(
                        MeasurementModel,
                        time,
                        defaults,
                        harvester_well_data,
                        measurement[self.measurement_value_key],
                        unit
                    )
                    self.updated = True
                if data['next']:
                    self._process_measurements(
                        data['next'], harvester_well_data, MeasurementModel,
                        parameter, unit
                    )
        else:
            pass
