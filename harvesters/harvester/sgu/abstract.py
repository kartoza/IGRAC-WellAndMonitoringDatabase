import json

import requests
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    HarvesterWellData, Harvester
)
from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class SkipProcessWell(Exception):
    """Raised when a Well is skipped."""
    pass


class SguAPI(BaseHarvester):
    """Harvester for https://www.sgu.se/"""
    countries = []
    crs = None

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.countries = []
        self.crs = None
        super(SguAPI, self).__init__(harvester, replace, original_id)

    @staticmethod
    def additional_attributes() -> dict:
        """Attributes that needs to be saved on database.
        The value is the default value for the attribute.
        """
        return {}

    def get_stations(self) -> list[dict]:
        """Retrieves station data from Harvester.

        :return: Station data from Harvester and csr.
        :rtype: list, str
        """
        url = 'https://apps.sgu.se/grundvattennivaer-rest/stationer'
        self._update('Fetching {}'.format(url))

        response = requests.get(url)
        if response.status_code == 404:
            return
        data = json.loads(response.text)
        self.crs = data['crs']['properties']['name']
        return data['features']

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        to_coord = SpatialReference(4326)
        from_coord = SpatialReference(self.crs)
        trans = CoordTransform(from_coord, to_coord)
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=self.crs)
        point.transform(trans)

        # check the station
        station_id = station['properties']['OMR_STN']
        name = station['properties']['STN_NAMN']
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=name,
            latitude=point.y,
            longitude=point.x,
        )
        return harvester_well_data

    def well_updated(self, well: Well):
        """When the well is updated."""
        self.post_processing_well(
            well, generate_country_cache=False
        )
        self.countries.append(well.country.code)

    def process_well(
            self, harvester_well_data: HarvesterWellData, note: str
    ):
        """Processing well."""
        raise NotImplementedError()

    def _process(self):
        """ Run the harvester """
        # get csr
        stations = self.get_stations()
        total = len(stations)

        # ------------------------------------------
        # STATIONS
        # ------------------------------------------
        for well_idx, station in enumerate(stations):
            try:
                harvester_well_data = self.well_from_station(station)
                well = harvester_well_data.well
            except (KeyError, TypeError, Well.DoesNotExist):
                continue

            try:
                self.process_well(
                    harvester_well_data,
                    f'Saving {well.original_id} : well({well_idx + 1}/{total})'
                )
            except SkipProcessWell:
                pass

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)
