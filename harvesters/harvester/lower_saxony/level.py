"""Harvester of using hubeau."""

import requests

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterParameterMap
)


class LowerSaxonyHarvester(BaseHarvester):
    """Lower Saxony harvester."""

    api_key_key = 'api-key'

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
            self._update(
                (
                    f'Saving {well.original_id} :'
                    f' well({well_idx + 1}/{total})'
                )
            )

            if self.is_processing_station:
                print("Save measurements")
