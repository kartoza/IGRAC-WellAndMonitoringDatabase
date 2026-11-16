"""England - Environment Agency Water Quality Explorer API

API: https://environment.data.gov.uk/water-quality/api-docs
"""

import re
import time
from datetime import datetime

import requests
from django.contrib.gis.geos import GEOSGeometry
from django.db import close_old_connections
from django.db.models import Max

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models import Harvester, HarvesterFeatureTypeMap, HarvesterParameterMap
from gwml2.models.term import TermFeatureType, TermWellStatus
from gwml2.models.well import Unit, Well, WellQualityMeasurement
from gwml2.utilities import make_aware_local


class EnglandQualityHarvester(BaseHarvester):
    """England - Environment Agency Water Quality Explorer API

    API: https://environment.data.gov.uk/water-quality/api-docs
    """

    offset_attribute_key = "offset"
    current_parameter = "current-parameter"
    LIMIT = 250
    TIMEOUT = 120

    # Retry when the API returns 429 (Too Many Requests)
    MAX_RETRIES = 5
    RETRY_DELAY = 30

    # EA unit (lowercase) to IGRAC unit name
    UNIT_ALIASES = {
        "ug/l": "μg/L",
        "us/cm": "μS/cm",
        "cel": "°C",
        "no/100ml": "cfu per 100 ml",
        "no/ml": "cfu per mL",
        "mv": "mV H⁺/H₂",
    }

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        """England - Environment Agency Water Quality Explorer API"""
        self.statuses = {}
        self.units = {unit.name.lower(): unit for unit in Unit.objects.all()}
        self.feature_types = HarvesterFeatureTypeMap.get_json(harvester)
        if not self.feature_types:
            raise ValueError("HarvesterFeatureTypeMap is empty.")

        # One parameter can just be mapped from one key (determinand),
        # because the last measurement is checked per parameter
        HarvesterParameterMap.get_json(harvester, is_unique_parameter=True)

        # Determinand to be resumed, it is set on _process
        self.current_determinand = None
        super(EnglandQualityHarvester, self).__init__(harvester, replace, original_id)

    def _request(self, url: str, params: dict) -> list:
        """Request to the API and return the members.

        Retry when the API returns 429 (Too Many Requests).
        """
        for attempt in range(self.MAX_RETRIES):
            response = requests.get(
                url,
                params=params,
                headers={"Accept": "application/ld+json"},
                timeout=self.TIMEOUT,
            )
            if response.status_code == 429:
                delay = self.RETRY_DELAY * (attempt + 1)
                self._update(f"Too many requests, retry in {delay}s")
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json().get("member", [])
        raise Exception(f"Too many requests after {self.MAX_RETRIES} retries")

    def get_stations(self):
        """Return stations."""
        return self._request(
            "https://environment.data.gov.uk/water-quality/sampling-point",
            params={
                "limit": self.LIMIT,
                "skip": self.current_offset,
                "samplingPointType": ",".join(self.feature_types.keys()),
            },
        )

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

    def get_unit(self, unit_name: str | None) -> Unit | None:
        """Return Unit from the observation hasUnit.

        PHUNITS (pH) does not have unit.
        """
        if not unit_name or unit_name == "PHUNITS":
            return None
        # EA unit name to IGRAC unit name
        unit_name = self.UNIT_ALIASES.get(unit_name.lower(), unit_name)
        try:
            return self.units[unit_name.lower()]
        except KeyError:
            raise ValueError(f"Unit {unit_name} does not exist") from None

    @staticmethod
    def parse_measurement(measurement) -> tuple[datetime, float, str | None] | None:
        """Return (time, value, methodology) of the observation.

        Return None when it does not have time or value.
        """
        result = measurement.get("hasResult") or {}
        methodology = None
        if result.get("numericValue") is not None:
            value = result["numericValue"]
        elif result.get("upperBound") is not None:
            value = result["upperBound"]
            methodology = "below detection limit"
        elif result.get("lowerBound") is not None:
            value = result["lowerBound"]
            methodology = "above detection limit"
        else:
            return None

        phenomenon_time = measurement.get("phenomenonTime")
        if not phenomenon_time:
            return None
        try:
            measurement_time = datetime.fromisoformat(phenomenon_time)
        except ValueError:
            return None
        return measurement_time, value, methodology

    def get_measurements(
        self, station, determinand: str, offset=0, from_date: str | None = None
    ) -> list:
        """Return measurements."""
        original_id = station["notation"]
        params = {"limit": self.LIMIT, "skip": offset, "determinand": determinand}
        if from_date:
            params["dateFrom"] = from_date
        return self._request(
            (
                "https://environment.data.gov.uk/water-quality/sampling-point/"
                f"{original_id}/observation"
            ),
            params=params,
        )

    def process_measurements(self, station, well: Well, last_measurements: dict) -> bool:
        """Process measurements per determinand.

        When a determinand error, stop that determinand and continue to the next one.
        The current determinand is saved for resuming.
        """
        updated = False
        original_id = station["notation"]
        total_determinand = len(self.parameters)
        for idx, (determinand, parameter) in enumerate(self.parameters.items()):
            determinand_prefix = f"{original_id} - {determinand} ({idx + 1}/{total_determinand})"

            # If it resumed, skip until the current determinand
            if self.current_determinand:
                if determinand != self.current_determinand:
                    continue
                self.current_determinand = None
            self.update_attribute(self.current_parameter, determinand)

            measurement_parameter = parameter["parameter"]
            unit = parameter["unit"]
            last_measurement = last_measurements.get(measurement_parameter.id)
            from_date = last_measurement.date().isoformat() if last_measurement else None

            # Pull all pages first
            measurements = []
            offset = 0
            try:
                while True:
                    response_measurements = self.get_measurements(
                        station, determinand=determinand, offset=offset, from_date=from_date
                    )

                    # Convert to [time, value, methodology]
                    for measurement in response_measurements:
                        row = self.parse_measurement(measurement)
                        if not row:
                            continue
                        measurement_time, value, methodology = row
                        if last_measurement and make_aware_local(measurement_time) <= (
                            last_measurement
                        ):
                            continue
                        if not unit:
                            unit = self.get_unit(measurement.get("hasUnit"))
                        measurements.append([measurement_time, value, methodology])

                    self._update(
                        f"{determinand_prefix} : {offset + len(response_measurements)} measurements"
                    )
                    # Last page when returned less than limit
                    if len(response_measurements) < self.LIMIT:
                        break
                    offset += self.LIMIT

                # Save all after pulling everything
                self._update(f"{determinand_prefix} : found {len(measurements)}")
                if measurements:
                    self._bulk_save(
                        original_id,
                        well,
                        measurements,
                        WellQualityMeasurement,
                        measurement_parameter,
                        unit,
                    )
                    updated = True
            except Exception as e:
                # Stop this determinand
                self.log.log_well(original_id, "Error", f"{determinand} : {type(e).__name__}: {e}")
                continue

        # All determinands are done for this well
        self.delete_attribute(self.current_parameter)
        return updated

    def _process(self):
        """Run the harvester."""
        # Get latest offset
        self.current_offset = int(self.attributes.get(self.offset_attribute_key, "0"))

        # Get latest determinand, just when it is still on the parameters
        self.current_determinand = self.attributes.get(self.current_parameter, None)
        if self.current_determinand not in self.parameters:
            self.current_determinand = None

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

                # Drop the broken connection, Django reconnects on the next query.
                close_old_connections()

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

                    well_updated = False

                    # If feature type changed
                    if well.feature_type != feature_type:
                        well.feature_type = feature_type
                        well_updated = True

                    # Save well status
                    status = self.get_status(station)
                    if status and well.status != status:
                        well.status = status
                        well_updated = True

                    if well_updated:
                        well.save()

                    # Last measurements
                    last_measurements = dict(
                        well.wellqualitymeasurement_set.values("parameter_id")
                        .annotate(last_time=Max("time"))
                        .values_list("parameter_id", "last_time")
                    )

                    # Process measurements
                    measurement_updated = self.process_measurements(
                        station, well, last_measurements
                    )
                    if not measurement_updated:
                        self.log.log_well(original_id, "Empty", "No measurements found")

                    # Post processing once when well or measurements are updated
                    if well_updated or measurement_updated:
                        self.post_processing_well(well)
                except Exception as e:
                    self.log.log_well(original_id, "Error", f"{type(e).__name__}: {e}")
                finally:
                    # Resume determinand is just for the first processed well
                    self.current_determinand = None

            self.current_offset += self.LIMIT
            self.update_attribute(self.offset_attribute_key, self.current_offset)

        # Reset so the following caches/done logs in base are not prefixed
        self.log_prefix = ""
        self.delete_attribute(self.offset_attribute_key)
        self.delete_attribute(self.current_parameter)
