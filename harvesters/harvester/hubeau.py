"""Harvester of using hubeau."""

import requests
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    Well, MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement
)


class Hubeau(BaseHarvester):
    """
    Harvester for https://hubeau.eaufrance.fr/page/api-piezometrie
    """
    domain = 'https://hubeau.eaufrance.fr/api/v1/niveaux_nappes'
    original_id_key = 'code_bss'

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

        # Process the stations
        self._process_stations(
            f'https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations?code_bss=0024%2FS&code_bss=00353X0073%2FP&code_bss=00512X0001%2FP1&code_bss=00771X0030%2FP&code_bss=01277X0192%2FS1&code_bss=01551X1006%2FS1&code_bss=03152X0027%2FF&code_bss=03212X0021%2FP&code_bss=03276X0009%2FP&code_bss=03375X0013%2FP1&code_bss=04987X0022%2FP&code_bss=05867X0152%2FSR1&code_bss=07155X0016%2FP1&code_bss=07475X0008%2FF3&code_bss=07844X0076%2FP1&code_bss=08266X0136%2FF&code_bss=09503X0057%2FF2&code_bss=09655X0265%2FCLOS&code_bss=10247X0096%2FP&code_bss=10592X0012%2FAEP&format=json&size=20'
        )
        self._done('Done')

    def _measurement_url(self, params_dict: dict):
        """Construct url for measurement"""
        measurement_params = {
            'size': 500,
            'fields': 'date_mesure,profondeur_nappe',
            'sort': 'asc',
        }
        measurement_params.update(params_dict)

        params = []
        for key, value in measurement_params.items():
            params.append(f'{key}={value}')
        return f'{self.domain}/chroniques_tr?{"&".join(params)}'

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
                geometry = station['geometry']
                if not geometry or not geometry['coordinates']:
                    continue
                latitude = geometry['coordinates'][1]
                longitude = geometry['coordinates'][0]

                params = {
                    'bss_id': station['bss_id']
                }
                original_id = station[self.original_id_key]
                well = self.get_well(original_id, latitude, longitude)
                if well:
                    last_measurement = well.welllevelmeasurement_set.first()
                    if last_measurement:
                        last_date = last_measurement.time.strftime("%Y-%m-%d")
                        params.update(
                            {
                                'date_debut_mesure': last_date
                            }
                        )
                else:
                    if not self.harvester.save_missing_well:
                        continue

                # Process measurement
                try:
                    self._process_measurements(
                        self._measurement_url(params), station, None
                    )

                    # Generate cache
                    well = self.get_well(original_id, latitude, longitude)
                    if well:
                        self.post_processing_well(well)
                except Well.DoesNotExist:
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
                if data['next']:
                    self._process_measurements(
                        data['next'], station, harvester_well_data
                    )
        else:
            pass
