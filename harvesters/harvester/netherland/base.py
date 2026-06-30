"""Harvester for netherland."""

import requests
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.models import Well


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

    def get_original_id(self, feature: dict) -> str:
        """Return original id."""
        return f"{feature['properties']['bro_id']}"

    def well_from_station(self, station: dict) -> Well:
        """Retrieves well data from station."""
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=4326)

        # check the station
        station_id = self.get_original_id(station)
        well = self._save_well(
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
        return well

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
                    self.log.log_well(original_id, 'skip')
                    continue

                self._update(f'Saving {original_id}')
                updated, well = self.process_measurement(feature)

                if well and updated:
                    print(f'{original_id} : done')
                    self._update(f'Generate cache for {well.original_id}')
                    if well:
                        self.post_processing_well(well)

                if well is None:
                    status = 'empty'
                elif updated:
                    status = 'saved'
                else:
                    status = 'no_change'
                self.log.log_well(original_id, status)
            except (KeyError, TypeError, Well.DoesNotExist) as e:
                self.log.log_well(original_id, 'error', str(e))
                continue
            except Exception as e:
                self.log.log_well(original_id, 'error', str(e))
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
