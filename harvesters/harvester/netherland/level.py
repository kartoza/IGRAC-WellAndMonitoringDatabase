"""Harvester for netherland."""

import csv
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO

import requests

from gwml2.harvesters.models import Harvester
from gwml2.models import (
    MEASUREMENT_PARAMETER_AMSL,
    TermMeasurementParameter,
    Unit,
    WellLevelMeasurement,
)

from .base import NetherlandHarvester


class NetherlandLevelHarvester(NetherlandHarvester):
    """https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gld."""

    countries = []

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        self.level_parameter = TermMeasurementParameter.objects.get(name=MEASUREMENT_PARAMETER_AMSL)
        try:
            self.unit = Unit.objects.get(name="m")
        except Unit.DoesNotExist:
            raise Exception("Unit m does not exist")
        super(NetherlandLevelHarvester, self).__init__(harvester, replace, original_id)

    @property
    def station_url(self):
        """Return station url."""
        return (
            "https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gld/items?"
            "f=json&limit=1000&crs=http://www.opengis.net/def/crs/OGC/1.3/CRS84"
        )

    def process_measurement(self, station):
        """Processing level measurement."""
        original_id = self.get_original_id(station)
        response = requests.get(
            f"https://publiek.broservices.nl/gm/gld/v1/seriesAsCsv/{original_id}"
        )
        csv_data = StringIO(response.text)
        rows = list(csv.DictReader(csv_data))

        total = len(rows)
        self._update(f"{original_id} : processing {total} rows")

        # Parse valid rows
        valid_rows = []
        for row in rows:
            try:
                value = (
                    row["Beoordeelde Waarde [m]"]
                    or row["Controle Waarde [m]"]
                    or row["Voorlopige Waarde [m]"]
                    or row["Onbekend Waarde [m]"]
                )

                if not row["Tijdstip"] or not value:
                    continue

                date_time = datetime.fromtimestamp(
                    float(row["Tijdstip"]) / 1000,
                    tz=timezone.utc,
                )
                valid_rows.append((date_time, float(value)))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Failed to parse row {row}: {e}") from e

        if not valid_rows:
            return False, None

        # Aggregate to one reading per day: average value, time at 00:00:00
        daily_values = defaultdict(list)
        for dt, val in valid_rows:
            midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_values[midnight].append(val)
        valid_rows = sorted(
            (midnight, sum(vals) / len(vals)) for midnight, vals in daily_values.items()
        )
        self._update(f"{original_id} : aggregated to {len(valid_rows)} daily rows")

        well = self.well_from_station(station)
        last_measurement = (
            well.welllevelmeasurement_set.order_by("-time").values_list("time", flat=True).first()
        )
        self._update(f"{original_id} : last measurement {last_measurement}")

        seen = set()
        rows_to_save = []
        for dt, val in valid_rows:
            if last_measurement and dt <= last_measurement:
                continue
            if dt not in seen:
                seen.add(dt)
                rows_to_save.append((dt, val))
        self._update(f"{original_id} : {len(rows_to_save)} new rows to save")

        if not rows_to_save:
            return False, well

        self._bulk_save(
            original_id, well, rows_to_save, WellLevelMeasurement, self.level_parameter, self.unit
        )
        return True, well
