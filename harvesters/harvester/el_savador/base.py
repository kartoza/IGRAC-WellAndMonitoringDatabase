"""Harvester of using hubeau."""
import json
from datetime import datetime

import requests
from dateutil.parser import parse
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    HarvesterWellData, Harvester
)
from gwml2.models import (
    Unit, TermMeasurementParameter, MEASUREMENT_PARAMETER_AMSL
)
from gwml2.models.well import (
    WellLevelMeasurement, WellQualityMeasurement
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class ElSavadorHarvester(BaseHarvester):
    """Rwanda harvester.

    https://srt.snet.gob.sv/apidoa/api/sihi/DataPozos/puntosagua
    """
    api_key_key = 'api-key'
    updated = False
    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.level_parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        self.level_unit = Unit.objects.get(name='m')
        self.temperature_parameter = TermMeasurementParameter.objects.get(
            name='T'
        )
        self.temperature_unit = Unit.objects.get(name='°C')
        super(ElSavadorHarvester, self).__init__(
            harvester, replace, original_id
        )

    def _get_station(self, row):
        """Return stations."""
        identifier = row['codPuntoAgua']
        name = row['nombre']
        point = Point(
            row['loc']['coordinates'][0], row['loc']['coordinates'][1],
            srid=4326
        )
        z = row['z']

        # check the station
        return self._save_well(
            original_id=identifier,
            name=name,
            latitude=point.y,
            longitude=point.x,
            ground_surface_elevation_masl=z
        )

    def _process(self):
        """Process the harvester.

        Rwanda does not have method to harvest new well.
        """
        print(f"Fetching stations")
        response = requests.get(
            'https://srt.snet.gob.sv/apidoa/api/sihi/DataPozos/puntosagua'
        )
        for row in response.json():
            original_id = row['idPuntoAgua']
            identifier = row['codPuntoAgua']
            name = row['nombre']
            if not name:
                continue

            # We check the measurements
            first_time = "2000-01-01T00:00:00"

            # Well is already saved
            well = self.get_well(
                identifier,
                latitude=row['loc']['coordinates'][1],
                longitude=row['loc']['coordinates'][0]
            )
            if well and well.last_time_measurement:
                try:
                    # If it has HarvesterWellData
                    # Use last_time_measurement
                    # As we need temperature data
                    HarvesterWellData.objects.get(
                        harvester=self.harvester, well=well
                    )
                    first_time = well.last_time_measurement.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                except HarvesterWellData.DoesNotExist:
                    pass
            if not self.harvester.save_missing_well and not well:
                print(
                    f"Station {identifier} ({original_id}) "
                    f"not found as we don't need to save missing wells."
                )
                continue

            payload = {
                "idPuntoAgua": original_id,
                "fecha1": first_time,
                "fecha2": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }

            print(f"----------------------------------------")
            print(f"Fetching measurements for {identifier} ({original_id})")
            print(f"Payload : {json.dumps(payload)}")
            measurements_response = requests.post(
                'https://srt.snet.gob.sv/apidoa/api/sihi/DataPozos/'
                'niveles_puntoagua/',
                json=payload
            )
            if measurements_response.status_code != 200:
                print(
                    f"ERROR: POST failed for {identifier} "
                    f"- status {measurements_response.status_code}: "
                    f"{measurements_response.text}"
                )
                continue

            measurements = measurements_response.json()
            if not measurements:
                print(f"No measurements for {identifier}, skipping")
                continue

            updated = False
            print(f"Found {len(measurements)} measurements for {identifier}")
            well, harvester_well_data = self._get_station(row)
            for measurement in measurements:
                time = parse(measurement['fecha'])
                # ---------------------------------------
                # LEVEL MEASUREMENT
                # ---------------------------------------
                level = measurement['nivel']
                if level:
                    defaults = {
                        'parameter': self.level_parameter
                    }
                    self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        level,
                        self.level_unit
                    )
                    updated = True

                # ---------------------------------------
                # TEMPERATURE MEASUREMENT
                # ---------------------------------------
                temperature = measurement['temperatura']
                if temperature:
                    defaults = {
                        'parameter': self.temperature_parameter
                    }
                    self._save_measurement(
                        WellQualityMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        temperature,
                        self.temperature_unit
                    )
                    updated = True

            if updated:
                # -----------------------
                # Generate cache
                if well and updated:
                    self.post_processing_well(
                        well, generate_country_cache=False
                    )
                    if well.country:
                        self.countries.append(well.country.code)

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)
