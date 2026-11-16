"""England - Environment Agency Water Quality Explorer API

API: https://environment.data.gov.uk/water-quality/api-docs
"""

import re

import requests
from django.contrib.gis.geos import GEOSGeometry

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models import Harvester, HarvesterFeatureTypeMap
from gwml2.models.term import TermFeatureType, TermWellStatus


class EnglandQualityHarvester(BaseHarvester):
    """England - Environment Agency Water Quality Explorer API

    API: https://environment.data.gov.uk/water-quality/api-docs
    """

    offset_attribute_key = "offset"
    LIMIT = 250
    TIMEOUT = 120

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        """England - Environment Agency Water Quality Explorer API"""
        self.statuses = {}
        self.feature_types = HarvesterFeatureTypeMap.get_json(harvester)
        if not self.feature_types:
            raise ValueError("HarvesterFeatureTypeMap is empty.")

        super(EnglandQualityHarvester, self).__init__(harvester, replace, original_id)

    def get_stations(self):
        """Return stations."""
        response = requests.get(
            "https://environment.data.gov.uk/water-quality/sampling-point",
            params={
                "limit": self.LIMIT,
                "skip": self.current_offset,
                "samplingPointType": ",".join(self.feature_types.keys()),
            },
            headers={"Accept": "application/ld+json"},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("member", [])

    def get_status(self, station) -> TermWellStatus | None:
        """Return TermWellStatus from station status label.

        Just return if it is found on TermWellStatus.
        """
        status = station.get("samplingPointStatus", {})
        label = status.get("prefLabel")
        if not label:
            return None
        key = label.lower()
        if key not in self.statuses:
            self.statuses[key] = TermWellStatus.objects.filter(name__iexact=label).first()
        if self.statuses[key]:
            return self.statuses[key]
        return None

    def get_feature_type(self, station) -> TermFeatureType | None:
        """Return TermFeatureType from samplingPointType notation.

        BA = Groundwater - Borehole -> water well
        BB = Groundwater - Spring -> spring
        BC = Groundwater - Wells & Adit -> water well
        The notation is mapped through HarvesterFeatureTypeMap,
        raise an error if it is not configured.
        """
        original_id = station["notation"]
        _type = station.get("samplingPointType", {})
        notation = _type.get("notation")
        if not notation:
            raise ValueError(f"Station {original_id} does not have samplingPointType")
        try:
            return self.feature_types[notation]
        except KeyError:
            raise ValueError(f"Feature type map for {notation} is not configured") from None

    @staticmethod
    def get_coordinates(station) -> tuple[float, float]:
        """Return (latitude, longitude) in EPSG:4326 from geometry.asWKT.

        Example asWKT:
        "POINT(527000 239780) <http://www.opengis.net/def/crs/EPSG/0/27700>"
        """
        as_wkt = (station.get("geometry") or {}).get("asWKT")
        if not as_wkt:
            raise ValueError("Station does not have geometry")

        # Split WKT and optional CRS URI
        match = re.match(r"^\s*(.+?)\s*(?:<([^>]+)>)?\s*$", as_wkt)
        wkt, crs_uri = match.group(1), match.group(2)
        srid = 4326
        if crs_uri:
            srid_match = re.search(r"EPSG/\d+/(\d+)", crs_uri)
            if srid_match:
                srid = int(srid_match.group(1))

        point = GEOSGeometry(wkt, srid=srid)
        if srid != 4326:
            point.transform(4326)
        return point.y, point.x

    def _process(self):
        """Run the harvester."""
        # Get latest offset
        self.current_offset = int(self.attributes.get(self.offset_attribute_key, "0"))

        while True:
            self._update(f"Fetching stations : offset {self.current_offset}")
            stations = self.get_stations()

            # If empty, break the loop
            if not stations:
                break

            # Loop the station
            total = len(stations)
            for idx, station in enumerate(stations):
                self.log_prefix = f"{idx + 1}/{total} offset - {self.current_offset}"
                original_id = station["notation"]

                # Check the well
                # If it resumed and not the current one, skip it
                self.check_current_well(original_id)
                if not self.is_processing_station:
                    continue

                try:
                    name = station["prefLabel"]
                    latitude, longitude = self.get_coordinates(station)
                    feature_type = self.get_feature_type(station)

                    # Save to well
                    well = self._save_well(
                        original_id=original_id,
                        name=name,
                        latitude=latitude,
                        longitude=longitude,
                        feature_type=feature_type,
                    )

                    updated = False

                    # If feature type changed
                    if well.feature_type != feature_type:
                        well.feature_type = feature_type
                        updated = True

                    # Save well status
                    status = self.get_status(station)
                    if status and well.status != status:
                        well.status = status
                        updated = True

                    # When updated, save and post processing
                    if updated:
                        well.save()
                        self.post_processing_well(well)

                    # Process measurements
                    # updated = self.process_measurements(station, well)
                    # if updated:
                    #     self.post_processing_well(well)
                    # else:
                    #     self.log.log_well(original_id, "Empty", "No measurements found")
                except Exception as e:
                    self.log.log_well(original_id, "Error", str(e))

            self.current_offset += self.LIMIT
            self.update_attribute(self.offset_attribute_key, self.current_offset)

        # Reset so the following caches/done logs in base are not prefixed
        self.log_prefix = ""
        self.delete_attribute(self.offset_attribute_key)
