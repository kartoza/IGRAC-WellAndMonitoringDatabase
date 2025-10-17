"""Harvester of using hubeau."""

import requests
from dateutil import parser
from dateutil.utils import today
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterParameterMap, HarvesterWellData
)
from gwml2.models import (
    Well, TermMeasurementParameter, Unit, TermMeasurementParameterGroup
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class RwandaHarvester(BaseHarvester):
    """Rwanda harvester.

    https://waterportal.rwb.rw/data/ground_water
    """
    api_key_key = 'api-key'
    updated = False
    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameters = HarvesterParameterMap.get_json(harvester)
        super(RwandaHarvester, self).__init__(
            harvester, replace, original_id
        )

    def _get_stations(self):
        """Return stations."""
        response = requests.post(
            'https://www.waterapi.rwb.rw/getTimeSeriesDescriptionList',
            json={
                "apikey": self.api_key
            }
        )
        location_identifiers = []
        for description in response.json()['TimeSeriesDescriptions']:
            identifier = description['Identifier'].split('@')[0]
            try:
                self.parameters[identifier]  # noqa
                location_identifiers.append(description['LocationIdentifier'])
            except Exception:
                pass
        return list(set(location_identifiers))

    def _get_station(self, identifier):
        """Return station."""
        response = requests.post(
            'https://www.waterapi.rwb.rw/getLocationData',
            json={
                "apikey": self.api_key,
                "locationIdentifier": identifier
            }
        )
        station = response.json()
        for tag in station["Tags"]:
            if tag["Key"] == "Groundwater":
                point = Point(
                    station["Longitude"], station["Latitude"], srid=4326
                )

                # check the station
                well, harvester_well_data = self._save_well(
                    original_id=identifier,
                    name=station["LocationName"],
                    latitude=point.y,
                    longitude=point.x,
                )
                return well
        return None

    def _process(self):
        """Process the harvester.

        Rwanda does not have method to harvest new well.
        """
        try:
            self.api_key = self.attributes[self.api_key_key]
        except KeyError:
            raise Exception('No api-key found in attributes.')

        if not self.parameters.keys():
            raise Exception('No parameter found in parameter map.')

        stations_identifiers = self._get_stations()
        wells = Well.objects.filter(
            organisation=self.harvester.organisation
        )
        for station_identifier in stations_identifiers:
            try:
                well = wells.filter(original_id=station_identifier).first()
                if not well:
                    well = self._get_station(station_identifier)
                if not well:
                    continue

                updated = False
                well, harvester_well_data = self._save_well(
                    original_id=well.original_id,
                    name=well.name,
                    latitude=well.location.y,
                    longitude=well.location.x
                )
                if not self.is_processing_station:
                    continue

                try:
                    response = requests.post(
                        'https://www.waterapi.rwb.rw/getTimeSeriesDescriptionList',
                        json={
                            "apikey": self.api_key,
                            "locationIdentifier": well.original_id,
                        }
                    )
                    time_series = response.json()['TimeSeriesDescriptions']
                    self._update(f'Saving {well.original_id}')
                    for description in time_series:
                        identifier = description[
                            'Identifier'].split('@')[0]
                        try:
                            parameter = self.parameters[identifier]
                            updated = self.process_measurement(
                                harvester_well_data,
                                description['UniqueId'],
                                parameter['parameter'],
                                parameter['unit']
                            )
                        except Exception:
                            pass

                except Exception:
                    continue

                if updated:
                    # -----------------------
                    # Generate cache
                    if well:
                        self.post_processing_well(
                            well, generate_country_cache=False
                        )
                        if well.country:
                            self.countries.append(well.country.code)

            except Well.DoesNotExist:
                pass

        # ------------------------------------
        # Run country caches
        # ------------------------------------
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_measurement(
            self, harvester_well_data: HarvesterWellData, unique_id,
            parameter: TermMeasurementParameter,
            unit: Unit
    ):
        """Save measurements."""
        data = {
            "apikey": self.api_key,
            "timeSeriesUniqueId": unique_id
        }
        first = harvester_well_data.well.wellqualitymeasurement_set.filter(
            parameter=parameter).first()
        if first:
            data['startTime'] = first.time.isoformat()
            data['endTime'] = today().isoformat()
        response = requests.post(
            'https://www.waterapi.rwb.rw/getTimeSeriesData',
            json=data
        )
        updated = False
        for point in response.json()['Points']:
            defaults = {
                'parameter': parameter
            }
            MeasurementModel = (
                TermMeasurementParameterGroup.get_measurement_model(
                    parameter
                )
            )
            self._save_measurement(
                MeasurementModel,
                parser.isoparse(point["Timestamp"]),
                defaults,
                harvester_well_data,
                point["NumericValue1"],
                unit
            )
            updated = True
        return updated
