"""Harvester of using Cida."""

from datetime import datetime, timezone

import requests
from dateutil.parser import parse

from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement
)
from .base import CidaUsgsApi


class CidaUsgsWaterLevel(CidaUsgsApi):
    """Harvester for https://cida.usgs.gov/ngwmn/index.jsp"""

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND
        )
        super(CidaUsgsWaterLevel, self).__init__(
            harvester, replace, original_id
        )

    @staticmethod
    def cql_filter_method():
        """Return station url."""
        return "((WL_SN_FLAG = '1') AND ((WL_WELL_TYPE = '1') OR (WL_WELL_TYPE = '2')))"

    @property
    def cql_filter(self):
        """Return station url."""
        return CidaUsgsWaterLevel.cql_filter_method()

    def get_measurements(self, well_data, well):
        """Get and save measurements."""
        site_id = well_data['site_id']
        agency_code = well_data['agency_code']

        last_time = well.welllevelmeasurement_set.order_by(
            '-time').values_list('time', flat=True).first()

        now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        start = (
            last_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            if last_time else '1900-01-01T00:00:00Z'
        )

        url = (
            'https://api.waterdata.usgs.gov/ngwmn/ogcapi/collections'
            f'/waterLevelObs/items?f=json&lang=en-US&limit=100'
            f'&datetime={start}/{now}'
            f'&monitoring_location_id={site_id}'
            f'&data_provided_by={agency_code}'
        )

        saved = 0
        while url:
            response = requests.get(url)
            if response.status_code != 200:
                self._update(f'{site_id} : Measurements not found')
                break

            data = response.json()
            features = data.get('features', [])
            if not features:
                break

            self._update(
                f'{site_id} : Processing {len(features)} measurements'
            )

            for feature in features:
                try:
                    props = feature['properties']
                    time = parse(props['sample_time'])
                    value = float(props['orig_value'])
                    unit = self.units[props['orig_unit'].lower()]
                    value, unit = self.change_value_to_meter(value, unit)
                    saved += 1
                    self._update(f'{site_id} : saving {saved} - {time}')
                    self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        {'parameter': self.parameter},
                        well,
                        value,
                        unit
                    )
                    self.updated = True
                except (ValueError, KeyError, TypeError):
                    pass

            url = next(
                (
                    link['href'] for link in data.get('links', [])
                    if link.get('rel') == 'next'
                ),
                None
            )
