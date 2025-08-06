"""Harvester of using Cida."""

import requests
from bs4 import BeautifulSoup
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
        super(CidaUsgsWaterLevel, self).__init__(harvester, replace, original_id)

    @staticmethod
    def cql_filter_method():
        """Return station url."""
        return "((WL_SN_FLAG = '1') AND ((WL_WELL_TYPE = '1') OR (WL_WELL_TYPE = '2')))"

    @property
    def cql_filter(self):
        """Return station url."""
        return CidaUsgsWaterLevel.cql_filter_method()

    def get_measurements(self, well_data, harvester_well_data):
        """Get and save measurements."""
        url = (
            f'https://cida.usgs.gov/ngwmn_cache/direct/flatXML/waterlevel/'
            f'{well_data["agency_code"]}/{well_data["site_no"]}'
        )
        response = requests.get(url)
        if response.status_code != 200:
            print('Measurements not found')
        else:
            xml = BeautifulSoup(response.content, "lxml")
            samples = xml.findAll('sample')
            count = len(samples)
            print(f'Measurements found : {count}')
            last_time = None
            last_data = harvester_well_data.well.welllevelmeasurement_set.all().first()
            if last_data:
                last_time = last_data.time

            for idx, measurement in enumerate(samples):
                try:
                    time = self.value_by_tag(measurement, 'time')
                    time = parse(time)
                    if last_time and time <= last_time:
                        continue

                    print(f'{idx}/{count} - {time}')
                    unit = self.units[
                        self.value_by_tag(measurement, 'unit').lower()
                    ]
                    value = float(
                        self.value_by_tag(
                            measurement, 'from-landsurface-value'
                        )
                    )
                    value, unit = self.change_value_to_meter(value, unit)
                    defaults = {
                        'parameter': self.parameter
                    }
                    self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        value,
                        unit
                    )
                    self.updated = True
                except (ValueError, KeyError, TypeError) as e:
                    pass
