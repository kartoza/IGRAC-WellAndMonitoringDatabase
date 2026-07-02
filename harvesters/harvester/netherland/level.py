"""Harvester for netherland."""

import csv
from datetime import datetime, timezone
from io import StringIO

import requests

from gwml2.harvesters.models import Harvester
from gwml2.models import (
    TermMeasurementParameter, MEASUREMENT_PARAMETER_AMSL, Unit,
    WellLevelMeasurement
)
from gwml2.models.general import Quantity
from gwml2.utilities import make_aware_local
from .base import NetherlandHarvester

CHUNK_SIZE = 1000


class NetherlandLevelHarvester(NetherlandHarvester):
    """https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gld."""

    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.level_parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        try:
            self.unit = Unit.objects.get(name='m')
        except Unit.DoesNotExist:
            raise Exception('Unit m does not exist')
        super(NetherlandLevelHarvester, self).__init__(
            harvester, replace, original_id
        )

    @property
    def station_url(self):
        """Return station url."""
        return (
            'https://api.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/ogc/v1/collections/gm_gld/items?'
            'f=json&limit=1000&crs=http://www.opengis.net/def/crs/OGC/1.3/CRS84'
        )

    def _bulk_save(self, original_id, well, rows_to_save):
        """Bulk insert measurements in chunks."""
        total = len(rows_to_save)
        saved = 0
        for start in range(0, total, CHUNK_SIZE):
            chunk = rows_to_save[start:start + CHUNK_SIZE]
            self._update(
                f'{original_id} : saving {start + 1}-'
                f'{min(start + CHUNK_SIZE, total)}/{total}'
            )
            quantities = Quantity.objects.bulk_create([
                Quantity(value=float(val), unit=self.unit)
                for _, val in chunk
            ])
            measurements = []
            for (dt, val), qty in zip(chunk, quantities):
                m = WellLevelMeasurement(
                    well=well,
                    time=make_aware_local(dt),
                    parameter=self.level_parameter,
                    value=qty,
                    value_in_m=float(val),
                )
                m.set_default_value()
                measurements.append(m)
            WellLevelMeasurement.objects.bulk_create(measurements)
            saved += len(chunk)
        return saved

    def process_measurement(self, station):
        """Processing level measurement."""
        original_id = self.get_original_id(station)
        response = requests.get(
            'https://publiek.broservices.nl/gm/gld/v1/seriesAsCsv/'
            f'{original_id}'
        )
        csv_data = StringIO(response.text)
        rows = list(csv.DictReader(csv_data))

        total = len(rows)
        self._update(f'{original_id} : processing {total} rows')

        # Parse valid rows
        valid_rows = []
        for row in rows:
            try:
                value = (
                        row['Beoordeelde Waarde [m]']
                        or row['Controle Waarde [m]']
                        or row['Voorlopige Waarde [m]']
                        or row['Onbekend Waarde [m]']
                )

                if not row['Tijdstip'] or not value:
                    continue

                date_time = datetime.fromtimestamp(
                    float(row['Tijdstip']) / 1000,
                    tz=timezone.utc,
                )
                valid_rows.append((date_time, value))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Failed to parse row {row}: {e}") from e

        if not valid_rows:
            return False, None

        well = self.well_from_station(station)
        last_measurement = well.welllevelmeasurement_set.order_by(
            '-time').values_list('time', flat=True).first()
        self._update(f'{original_id} : last measurement {last_measurement}')

        seen = set()
        rows_to_save = []
        for dt, val in valid_rows:
            if last_measurement and dt <= last_measurement:
                continue
            if dt not in seen:
                seen.add(dt)
                rows_to_save.append((dt, val))
        self._update(f'{original_id} : {len(rows_to_save)} new rows to save')

        if not rows_to_save:
            return False, well

        self._bulk_save(original_id, well, rows_to_save)
        return True, well
