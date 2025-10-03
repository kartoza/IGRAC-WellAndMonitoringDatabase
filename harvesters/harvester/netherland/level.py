"""Harvester for netherland."""

import csv
from datetime import datetime, timezone
from io import StringIO

import requests

from gwml2.harvesters.models import Harvester
from gwml2.harvesters.models.harvester import (
    HarvesterWellData
)
from gwml2.models import (
    TermMeasurementParameter, MEASUREMENT_PARAMETER_AMSL, Unit,
    WellLevelMeasurement
)
from .base import NetherlandHarvester


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

    def process_measurement(
            self,
            harvester_well_data: HarvesterWellData
    ):
        """Processing level measurement."""
        updated = False
        well = harvester_well_data.well
        response = requests.get(
            'https://publiek.broservices.nl/gm/gld/v1/seriesAsCsv/'
            f'{well.original_id}'
        )
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        rows = list(reader)

        last_measurement = well.welllevelmeasurement_set.order_by(
            '-time').first()
        for row in rows:
            if (
                    not row['Tijdstip'] or
                    (not row['Beoordeelde Waarde [m]'] and
                     not row['Voorlopige Waarde [m]'])
            ):
                continue
            date_time = datetime.fromtimestamp(
                float(row['Tijdstip']) / 1000, tz=timezone.utc
            )
            if last_measurement and date_time <= last_measurement.time:
                continue

            updated = True
            defaults = {
                'parameter': self.level_parameter,
            }
            value = row['Beoordeelde Waarde [m]'] or row[
                'Voorlopige Waarde [m]']
            self._save_measurement(
                WellLevelMeasurement,
                date_time,
                defaults,
                harvester_well_data,
                value,
                self.unit
            )
        return updated
