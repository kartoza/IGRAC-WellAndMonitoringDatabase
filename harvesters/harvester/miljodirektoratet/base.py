"""Harvester of using vannmiljoapi."""

import json

import requests
from dateutil import parser
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester, HarvestingError
from gwml2.harvesters.models.harvester import (
    HarvesterParameterMap, HarvesterWellData
)
from gwml2.models import (
    Well, TermMeasurementParameterGroup
)
from gwml2.models.general import Unit


class MiljodirektoratetHarvester(BaseHarvester):
    """Rwanda harvester.

    https://waterportal.rwb.rw/data/ground_water
    """
    api_key_key = 'api-key'
    ids_key = 'ids'
    updated = False
    countries = []

    def get_station(self, identifier) -> HarvesterWellData:
        """Return station."""
        response = requests.post(
            'https://vannmiljoapi.miljodirektoratet.no/api/'
            'Public/GetWaterLocations',
            headers={
                "vannmiljoWebAPIKey": self.api_key,
            },
            json={
                "WaterLocationIDFilter": [identifier]
            }
        )
        station = response.json()["Result"][0]
        point = Point(
            station["CoordX_dg"], station["CoordY_dg"], srid=4326
        )

        # check the station
        well, harvester_well_data = self._save_well(
            original_id=identifier,
            name=station["Name"],
            latitude=point.y,
            longitude=point.x,
        )
        return harvester_well_data

    def _process(self):
        """Process the harvester.

        Norway does not have method to harvest new well.
        """
        self.parameters = HarvesterParameterMap.get_json(self.harvester)
        try:
            self.ids = json.loads(self.attributes[self.ids_key])
        except KeyError:
            raise HarvestingError("No ids found in attributes")
        try:
            self.api_key = self.attributes[self.api_key_key]
        except KeyError:
            raise HarvestingError('No api-key found in attributes.')

        if not self.parameters.keys():
            raise Exception('No parameter found in parameter map.')

        total = len(self.ids)
        for idx, identifier in enumerate(self.ids):
            self._update(f'Processing : {identifier} {idx + 1}/{total}')
            if not self.is_processing_station and identifier == self.current_original_id:
                self.is_processing_station = True
            if not self.is_processing_station:
                continue
            try:
                harvester_well_data = None

                updated = False
                # process the station
                for key, value in self.parameters.items():
                    parameter = value['parameter']
                    defaults = {
                        'parameter': parameter
                    }
                    response = requests.post(
                        'https://vannmiljoapi.miljodirektoratet.no/'
                        'api/Public/GetRegistrations',
                        headers={
                            "vannmiljoWebAPIKey": self.api_key,
                        },
                        json={
                            "WaterLocationIDFilter": [identifier],
                            "ParameterIDFilter": [key]
                        }
                    )
                    measurements = response.json()["Result"]
                    for measurement in measurements:
                        unit = value['unit']
                        if not harvester_well_data:
                            harvester_well_data = self.get_station(identifier)

                        value_operator = measurement["ValueOperator"]
                        if value_operator != "=":
                            names = [
                                value_operator + unit.name,
                                value_operator + " " + unit.name
                            ]
                            unit = Unit.objects.filter(name__in=names).first()
                            if not unit:
                                continue
                        # Add the unit to the parameter
                        parameter.units.add(unit)
                        MeasurementModel = (
                            TermMeasurementParameterGroup.get_measurement_model(
                                parameter
                            )
                        )
                        self._save_measurement(
                            MeasurementModel,
                            parser.isoparse(measurement["SamplingTime"]),
                            defaults,
                            harvester_well_data,
                            measurement["RegValue"],
                            unit
                        )
                        updated = True
                    continue

                if updated:
                    # -----------------------
                    # Generate cache
                    if harvester_well_data:
                        self.post_processing_well(
                            harvester_well_data.well,
                            generate_country_cache=False
                        )
                        if harvester_well_data.well.country:
                            self.countries.append(
                                harvester_well_data.well.country.code
                            )
            except Well.DoesNotExist:
                pass
