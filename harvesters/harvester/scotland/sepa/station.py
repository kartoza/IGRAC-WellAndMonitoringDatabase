"""Harvester for Scotland Level Measurement.

API: https://timeseriesdoc.sepa.org.uk/api-documentation/
"""

from typing import Any

import requests
from django.contrib.gis.geos import Point


class Station:
    """Station data from sepa."""

    id: str
    name: str
    point: Point

    def __init__(self, id, name, latitude, longitude):
        """Initialize Station object."""
        self.id = id
        self.name = name
        self.point = Point(longitude, latitude, srid=4326)

    @staticmethod
    def fetch() -> list[dict[str, Any]]:
        """Fetch station data."""
        from .variables import GROUNDWATER_LEVEL_PARAMETER_ID

        url = (
            "https://timeseries.sepa.org.uk/KiWIS/KiWIS?"
            f"service=kisters&type=queryServices&datasource=0&request=getStationList&"
            f"format=geojson&parametertype_id={GROUNDWATER_LEVEL_PARAMETER_ID}"
        )
        response = requests.get(url)
        data = response.json()
        return data["features"]
