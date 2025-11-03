"""Harvester for netherland."""

import requests
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    HarvesterWellData
)
from gwml2.models import Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class NetherlandHarvester(BaseHarvester):
    """https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1."""

    countries = []

    @property
    def station_url(self):
        """Return station url."""
        raise NotImplementedError

    def _process(self):
        """ Run the harvester """
        self.fetch_stations(self.station_url)

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def get_original_id(self, feature: dict) -> str:
        """Return original id."""
        return f"{feature['properties']['bro_id']}"

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=4326)

        # check the station
        station_id = self.get_original_id(station)
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=station_id,
            latitude=point.y,
            longitude=point.x,
        )
        if not well.name or well.name == station_id:
            gm_gmw_monitoringtube_fk = station['properties'][
                'gm_gmw_monitoringtube_fk']
            response = requests.get(
                f'https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gmw_monitoringtube/items?f=json&limit=1&crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FOGC%2F1.3%2FCRS84&gm_gmw_monitoringtube_pk={gm_gmw_monitoringtube_fk}'
            )
            try:
                feature = response.json()['features']
                well.name = feature[0]['properties']['gmw_bro_id']
                print(f'Found name: {well.name}')
                well.save()
            except (KeyError, IndexError):
                pass
        return harvester_well_data

    def fetch_stations(self, url):
        """Fetch stations."""
        self._update(f'Fetching stations : {url}')
        response = requests.get(url)
        data = response.json()

        for feature in data['features']:
            original_id = self.get_original_id(feature)
            try:
                if not self.is_processing_station and original_id == self.current_original_id:
                    self.is_processing_station = True

                if not self.is_processing_station:
                    continue

                self._update(f'Saving {original_id}')
                updated, well = self.process_measurement(feature)

                if well and updated:
                    print(f'{original_id} : done')
                    # -----------------------
                    # Generate cache
                    if well:
                        self.post_processing_well(
                            well, generate_country_cache=False
                        )
                        if well.country:
                            self.countries.append(well.country.code)
            except (KeyError, TypeError, Well.DoesNotExist) as e:
                continue

        # next
        next_url = None
        for link in data['links']:
            try:
                if link['rel'] == 'next':
                    next_url = link['href']
                    break
            except KeyError:
                pass

        if next_url:
            self.fetch_stations(next_url)

    def process_measurement(self, station: dict):
        """Process measurement."""
        raise NotImplementedError
