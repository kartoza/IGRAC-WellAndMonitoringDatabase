"""Harvester of using hubeau."""

import re
from datetime import datetime, timezone

import requests

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterParameterMap
)
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class LowerSaxonyHarvester(BaseHarvester):
    """Lower Saxony harvester."""

    api_key_key = 'api-key'
    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameters = HarvesterParameterMap.get_json(harvester)
        super(LowerSaxonyHarvester, self).__init__(
            harvester, replace, original_id
        )

    def fetch_stations(self, url):
        """Fetch stations."""
        self._update(f'Fetching stations : {url}')
        response = requests.get(url)
        data = response.json()["getStammdatenResult"]
        return data

    def well_from_station(self, station: dict) -> dict:
        """Retrieves well data from station."""
        # check the station
        station_id = station['STA_ID']
        station_name = station['STA_Nummer']
        elevation = station['Hoehe']
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=station_name,
            latitude=station['WGS84Rechtswert'],
            longitude=station['WGS84Hochwert'],
            ground_surface_elevation_masl=elevation,
        )
        return well, harvester_well_data

    def _process(self):
        """Processing the data."""
        try:
            api_key = self.attributes[self.api_key_key]
        except KeyError:
            api_key = None
        if not api_key:
            raise Exception('No api-key found in attributes.')

        stations = self.fetch_stations(
            "https://bis.azure-api.net/GrundwasserstandonlinePublic/REST/"
            f"stammdaten/stationen/allegrundwasserstationen?key={api_key}"
        )
        total = len(stations)
        for well_idx, station in enumerate(stations):
            well, harvester_well_data = self.well_from_station(station)
            note = (
                f'Saving {well.original_id} :'
                f' well({well_idx + 1}/{total})'
            )
            self._update(note)

            updated = False
            if self.is_processing_station:
                # Parameter ids
                for param_id, parameter in self.parameters.items():
                    unit = parameter['unit']
                    parameter = parameter['parameter']
                    defaults = {
                        'parameter': parameter
                    }
                    MeasurementModel = (
                        TermMeasurementParameterGroup.get_measurement_model(
                            parameter
                        )
                    )
                    first = MeasurementModel.objects.filter(
                        well=well,
                        parameter=parameter
                    ).first()
                    tage = 18250
                    if first:
                        today = datetime.today().date()
                        tage = (today - first.time.date()).days

                    url = (
                        f"https://bis.azure-api.net/GrundwasserstandonlinePublic/"
                        f"REST/station/{well.original_id}/"
                        f"datenspuren/parameter/{param_id}/"
                        f"tage/-{tage}?key={api_key}"
                    )

                    response = requests.get(url)
                    measurements = []
                    for parameter in response.json()[
                        "getPegelDatenspurenResult"
                    ]["Parameter"]:
                        for result in parameter["Datenspuren"]:
                            for measurement in result["Pegelstaende"]:
                                date = None
                                match = re.search(
                                    r"/Date\((\d+)",
                                    measurement["DatumUTC"]
                                )
                                if match:
                                    timestamp_ms = int(match.group(1))
                                    date = datetime.fromtimestamp(
                                        timestamp_ms / 1000, tz=timezone.utc
                                    )
                                if date:
                                    if measurement[
                                        "Grundwasserstandsklasse"
                                    ] == "-":
                                        continue
                                    measurement = {
                                        "time": date,
                                        "value": measurement["Wert"]
                                    }
                                    measurements.append(measurement)
                    measurements.sort(key=lambda x: x["time"])
                    self._update(
                        f'{note} - Found measurements {len(measurements)}'
                    )
                    for measurement in measurements:
                        self._save_measurement(
                            MeasurementModel,
                            measurement['time'],
                            defaults,
                            harvester_well_data,
                            measurement['value'],
                            unit
                        )
                        updated = True

            if updated:
                # -----------------------
                # Generate cache
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
