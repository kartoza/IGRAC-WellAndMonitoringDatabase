"""England - Environment Agency Hydrology API

API: https://environment.data.gov.uk/hydrology/doc/reference
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import requests
from django.utils import timezone

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models import Harvester
from gwml2.models import (
    MEASUREMENT_PARAMETER_AMSL,
    TermMeasurementParameter,
    Unit,
    Well,
    WellLevelMeasurement,
)
from gwml2.models.general import Quantity
from gwml2.models.geology import Geology
from gwml2.models.term import TermReferenceElevationType, TermWellStatus
from gwml2.models.well import HydrogeologyParameter
from gwml2.utilities import make_aware_local


class EnglandLevelHarvester(BaseHarvester):
    """England - Environment Agency Hydrology API

    API: https://environment.data.gov.uk/hydrology/doc/reference
    """

    offset_attribute_key = "offset"
    LIMIT = 10000
    TIMEOUT = 120

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        """Save the harvester for England - Environment Agency Hydrology API."""
        self.level_parameter = TermMeasurementParameter.objects.get(name=MEASUREMENT_PARAMETER_AMSL)
        try:
            self.unit = Unit.objects.get(name="m")
        except Unit.DoesNotExist:
            raise Exception("Unit m does not exist")

        self.statuses = {}
        super(EnglandLevelHarvester, self).__init__(harvester, replace, original_id)

    def get_stations(self):
        """Return stations."""
        response = requests.get(
            "https://environment.data.gov.uk/hydrology/id/stations.json",
            params={
                "_limit": self.LIMIT,
                "observedProperty": "groundwaterLevel",
                "_offset": self.current_offset,
            },
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("items", [])

    def get_measurements(
        self,
        measurement_url: str,
        offset=0,
        from_date: str | None = "",
        date_param: str = "min-dateTime",
    ):
        """Return measurements."""
        measurement_url = measurement_url.replace("http://", "https://")
        params = {
            "_limit": self.LIMIT,
            "_offset": offset,
        }
        if from_date:
            params[date_param] = from_date
        response = requests.get(
            measurement_url + "/readings.json",
            params=params,
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("items", [])

    def get_status(self, station) -> TermWellStatus | None:
        """Return TermWellStatus from station status label.

        Just return if it is found on TermWellStatus.
        """
        statuses = station.get("status") or []
        if isinstance(statuses, dict):
            statuses = [statuses]
        for status in statuses:
            label = status.get("label") if isinstance(status, dict) else None
            if not label:
                continue
            key = label.lower()
            if key not in self.statuses:
                self.statuses[key] = TermWellStatus.objects.filter(name__iexact=label).first()
            if self.statuses[key]:
                return self.statuses[key]
        return None

    def process_measurements(self, station, well: Well) -> bool:
        """Process measurements."""
        updated = False
        measurement_types = [
            measure
            for measure in station.get("measures", [])
            if measure.get("parameter") == "level"
        ]
        default_measure_id = None
        for measure in measurement_types:
            measure_id = measure.get("@id", "")
            if "-gw-dipped-" in measure_id:
                default_measure_id = measure_id
                break

        if measurement_types and not default_measure_id:
            default_measure_id = measurement_types[0].get("@id", "")
        original_id = station["wiskiID"]

        # Save measurements
        if default_measure_id:
            # Logged is sub-daily data, it is saved as daily mean
            is_logged = "-gw-logged-" in default_measure_id
            offset = 0
            last_measurement: Optional[datetime] = (
                well.welllevelmeasurement_set.order_by("-time")
                .values_list("time", flat=True)
                .first()
            )
            from_date = None
            date_param = "min-dateTime"
            if last_measurement:
                if is_logged:
                    # Daily mean is saved at 00:00:00, start from the next day
                    from_date = (
                        timezone.localtime(last_measurement).date() + timedelta(days=1)
                    ).isoformat()
                    date_param = "mineq-date"
                else:
                    from_date = last_measurement.isoformat()
            self._update(
                f"Found measure for {original_id} : {default_measure_id} "
                f"with from date {from_date or 'start'}"
                f"{' (daily mean)' if is_logged else ''}"
            )

            # Pull all pages first
            measurements = []
            daily_values = defaultdict(list)
            while True:
                response_measurements = self.get_measurements(
                    default_measure_id,
                    offset=offset,
                    from_date=from_date,
                    date_param=date_param,
                )

                # Filter by quality and convert to [time, value]
                for measurement in response_measurements:
                    value = measurement.get("value", None)
                    quality = measurement.get("quality", None)
                    if not quality or value is None:
                        continue
                    time = self.parse_time(measurement)
                    if not time:
                        continue
                    if last_measurement and make_aware_local(time) <= last_measurement:
                        continue
                    if is_logged:
                        daily_values[time.date()].append(float(value))
                    else:
                        measurements.append([time, value])

                self._update(
                    f"{original_id} : pulled {offset + len(response_measurements)} readings"
                )
                # Last page when returned less than limit
                if len(response_measurements) < self.LIMIT:
                    break
                offset += self.LIMIT

            # Daily mean for logged
            if is_logged:
                today = timezone.localdate()
                for date in sorted(daily_values.keys()):
                    # Today is not complete yet, it will be saved on next run
                    if date >= today:
                        continue
                    values = daily_values[date]
                    measurements.append(
                        [
                            datetime.combine(date, datetime.min.time()),
                            sum(values) / len(values),
                        ]
                    )

            # Save all after pulling everything
            self._update(f"Found measurements : {len(measurements)}")
            if measurements:
                self._bulk_save(
                    original_id,
                    well,
                    measurements,
                    WellLevelMeasurement,
                    self.level_parameter,
                    self.unit,
                )
                updated = True
        return updated

    @staticmethod
    def parse_time(measurement) -> datetime | None:
        """Return time from dateTime, fallback to date at 00:00:00."""
        date_time = measurement.get("dateTime")
        if date_time:
            try:
                return datetime.fromisoformat(date_time)
            except ValueError:
                pass
        date = measurement.get("date")
        if date:
            try:
                return datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                pass
        return None

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
                original_id = station["wiskiID"]

                # Check the well
                # If it resumed and not the current one, skip it
                self.check_current_well(original_id)
                if not self.is_processing_station:
                    continue

                try:
                    name = station["label"]
                    latitude = station["lat"]
                    longitude = station["long"]
                    borehole_depth = station.get("boreholeDepth", None)
                    aquifer = station.get("aquifer", None)

                    # Save to well
                    well = self._save_well(
                        original_id=original_id,
                        name=name,
                        latitude=latitude,
                        longitude=longitude,
                    )
                    # Total depth
                    if borehole_depth is not None:
                        if not well.geology:
                            well.geology = Geology.objects.create(
                                reference_elevation=TermReferenceElevationType.objects.filter(
                                    name="Ground Surface Level ASL"
                                ).first()
                            )
                        geology = well.geology
                        if geology.total_depth:
                            geology.total_depth.value = float(borehole_depth)
                            geology.total_depth.unit = self.unit
                            geology.total_depth.save()
                        else:
                            geology.total_depth = Quantity.objects.create(
                                value=float(borehole_depth), unit=self.unit
                            )
                            geology.save()
                    # Aquifer
                    if aquifer:
                        if not well.hydrogeology_parameter:
                            well.hydrogeology_parameter = HydrogeologyParameter.objects.create()
                        well.hydrogeology_parameter.aquifer_name = aquifer
                        well.hydrogeology_parameter.save()

                    # Save well status
                    status = self.get_status(station)
                    if status:
                        well.status = status
                    well.save()

                    # Process measurements
                    updated = self.process_measurements(station, well)
                    if updated:
                        self.post_processing_well(well)
                    else:
                        self.log.log_well(original_id, "Empty", "No measurements found")
                except Exception as e:
                    self.log.log_well(original_id, "Error", str(e))

            self.current_offset += self.LIMIT
            self.update_attribute(self.offset_attribute_key, self.current_offset)

        # Reset so the following caches/done logs in base are not prefixed
        self.log_prefix = ""
        self.delete_attribute(self.offset_attribute_key)
