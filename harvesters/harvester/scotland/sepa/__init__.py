"""Harvester for Scotland Level Measurement.

API: https://timeseriesdoc.sepa.org.uk/api-documentation/
"""

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
    WellLevelMeasurement,
)

from .station import Station


class ScotlandSepaHarvester(BaseHarvester):
    """Scotland Sepa Level Measurement Harvester.

    API: https://timeseriesdoc.sepa.org.uk/api-documentation/
    """

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        """Save the harvester for scotland SEPA."""
        self.level_parameter = TermMeasurementParameter.objects.get(name=MEASUREMENT_PARAMETER_AMSL)
        try:
            self.unit = Unit.objects.get(name="m")
        except Unit.DoesNotExist:
            raise Exception("Unit m does not exist")
        super(ScotlandSepaHarvester, self).__init__(harvester, replace, original_id)

    def timeseries(self):
        """Retrieves timeseries data.

        Return dict by station_id.
        """
        from .variables import GROUNDWATER_LEVEL_PARAMETER_ID, TIMESERIES_NAME

        url = (
            "https://timeseries.sepa.org.uk/KiWIS/KiWIS?service=kisters&"
            "type=queryServices&"
            "datasource=0&request=getTimeseriesList&"
            f"parametertype_id={GROUNDWATER_LEVEL_PARAMETER_ID}&"
            "ts_name=Day.Mean&format=json&"
            "returnfields=station_id,station_name,ts_id,ts_name"
        )
        response = requests.get(url)
        data = response.json()
        timeseries = {}
        for _row in data:
            timeseries_name = _row[3]
            if timeseries_name != TIMESERIES_NAME:
                continue

            timeseries[_row[0]] = {
                "station_name": _row[1],
                "timeseries_id": _row[2],
            }
        return timeseries

    def _process(self):
        """Run the harvester."""
        self._update("Fetching stations")
        features = Station.fetch()

        # This is timeseries
        timeseries_by_station_id = self.timeseries()
        total = len(features)
        for idx, feature in enumerate(features):
            self.log_prefix = f"{idx + 1}/{total}"
            properties = feature["properties"]
            station = Station(
                id=properties["station_id"],
                name=properties["station_name"],
                latitude=properties["station_latitude"],
                longitude=properties["station_longitude"],
            )
            original_id = station.id
            try:
                try:
                    timeseries = timeseries_by_station_id[original_id]
                    if timeseries["station_name"] != station.name:
                        raise KeyError
                except KeyError:
                    continue

                # Check the well
                # If it resumed and not the current one, skip it
                self.check_current_well(original_id)
                if not self.is_processing_station:
                    continue

                # Save to well
                well = self._save_well(
                    original_id=station.id,
                    name=station.name,
                    latitude=station.point.y,
                    longitude=station.point.x,
                )

                # This is timeseries
                self._update(f"Storing timeseries for {original_id} with timeseries {timeseries}")

                # Save measurements
                measurement_url = (
                    "https://timeseries.sepa.org.uk/KiWIS/KiWIS?service=kisters&"
                    "type=queryServices&datasource=0&request=getTimeseriesValues&"
                    f"ts_id={timeseries['timeseries_id']}&format=json"
                )
                last_date = timezone.now().isoformat()
                last_measurement: Optional[datetime] = (
                    well.welllevelmeasurement_set.order_by("-time")
                    .values_list("time", flat=True)
                    .first()
                )
                self._update(f"{original_id} : last measurement {last_measurement or '- Nothing'}")
                params = {}
                if last_measurement:
                    params["from"] = (last_measurement + timedelta(seconds=1)).isoformat()
                    params["to"] = last_date
                else:
                    params["period"] = "complete"

                response = requests.get(measurement_url, params=params)
                # output ->
                # [
                #   {
                #     "ts_id": "63011010",
                #     "rows": "73",
                #     "columns": "Timestamp,Value",
                #     "data": [
                #       [
                #         "2026-08-24T00:00:00.000Z",
                #         95.24]
                #       ]
                #   }
                # ]
                rows_to_save = response.json()[0]["data"]
                self._update(f"{original_id} : bulk save {len(rows_to_save)}")
                if rows_to_save:
                    self._bulk_save(
                        original_id,
                        well,
                        rows_to_save,
                        WellLevelMeasurement,
                        self.level_parameter,
                        self.unit,
                    )
                    self.post_processing_well(well)
                else:
                    self.log.log_well(original_id, "Empty", "No measurements found")
            except Exception as e:
                self.log.log_well(original_id, "Error", str(e))

        # Reset so the following caches/done logs in base are not prefixed
        self.log_prefix = ""
