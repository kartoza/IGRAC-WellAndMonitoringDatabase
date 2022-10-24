"""Harvester of using hubeau."""

import requests
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement
)


class Hubeau(BaseHarvester):
    """
    Harvester for https://hubeau.eaufrance.fr/page/api-piezometrie
    """
    domain = 'https://hubeau.eaufrance.fr/api/v1/niveaux_nappes'

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
            f'{self.domain}/stations?'
            'format=json&nb_mesures_piezo_min=2&size=100'
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
        response = requests.get(url)
        if response.status_code in [200, 206]:
            data = response.json()
            stations = data['data']
            for station in stations:
                if not station['geometry'] \
                        or station['geometry']['coordinates']:
                    continue
                original_id = station['bss_id']
                latitude = station['geometry']['coordinates'][1]
                longitude = station['geometry']['coordinates'][0]

                params = {
                    'bss_id': original_id
                }
                well = self.get_well(original_id, latitude, longitude)
                if well:
                    last_measurement = well.welllevelmeasurement_set.order_by(
                        '-time'
                    ).first()
                    if last_measurement:
                        last_date = last_measurement.time.strftime("%Y-%m-%d")
                        params.update(
                            {
                                'date_debut_mesure': last_date
                            }
                        )

                self._process_measurements(
                    self._measurement_url(params), station, None
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
            original_id = station['bss_id']
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
