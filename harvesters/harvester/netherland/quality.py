"""Harvester for netherland."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import requests

from gwml2.harvesters.models import Harvester
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup
)
from .base import NetherlandHarvester


class NetherlandQualityHarvester(NetherlandHarvester):
    """https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gar."""

    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        super(NetherlandQualityHarvester, self).__init__(
            harvester, replace, original_id
        )

    @property
    def station_url(self):
        """Return station url."""
        return (
            'https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gar/items?'
            'f=json&limit=1000&crs=http://www.opengis.net/def/crs/OGC/1.3/CRS84'
        )

    def process_measurement(self, station):
        """Processing level measurement."""
        updated = False
        well = None
        original_id = self.get_original_id(station)
        try:
            response = requests.get(
                'https://publiek.broservices.nl/gm/gar/v1/objects/'
                f'{original_id}'
            )

            ns = {
                "garcommon": "http://www.broservices.nl/xsd/garcommon/1.0",
                "brocom": "http://www.broservices.nl/xsd/brocommon/3.0"
            }
            xml = ET.fromstring(response.content)

        except (ET.ParseError, requests.exceptions.RequestException):
            return False

        processes = xml.findall(".//garcommon:analysisProcess", namespaces=ns)
        for process in processes:
            date = process.find(".//brocom:date", namespaces=ns)
            if date is not None and date.text:
                dt = datetime.strptime(date.text, "%Y-%m-%d")
                time = datetime.fromtimestamp(
                    dt.timestamp(), tz=timezone.utc
                )
                analysis = process.findall(
                    ".//garcommon:analysis", namespaces=ns
                )
                for row in analysis:
                    parameter = row.find(
                        ".//garcommon:parameter", namespaces=ns
                    )
                    value = row.find(
                        ".//garcommon:analysisMeasurementValue", namespaces=ns
                    )
                    try:
                        if (
                                parameter is not None and parameter.text and
                                value is not None and value.text
                        ):
                            unit = self.parameters[parameter.text]['unit']
                            parameter = self.parameters[
                                parameter.text]['parameter']

                            # Get well when there is data
                            if not well:
                                harvester_well_data = self.well_from_station(
                                    station)
                                well = harvester_well_data.well

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
                                time,
                                defaults,
                                harvester_well_data,
                                float(value.text),
                                unit
                            )
                            updated = True
                    except KeyError:
                        pass

        return updated, well
