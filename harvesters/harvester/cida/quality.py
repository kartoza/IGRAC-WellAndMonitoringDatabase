"""Harvester of using Cida."""

from .base import CidaUsgsApi


class CidaUsgsWaterQuality(CidaUsgsApi):
    """Harvester for https://cida.usgs.gov/ngwmn/index.jsp."""

    @staticmethod
    def cql_filter_method():
        """Return station url."""
        return "((QW_SN_FLAG = '1') AND ((QW_WELL_TYPE = '1') OR (QW_WELL_TYPE = '2'))) AND SITE_NO=20772"

    @property
    def cql_filter(self):
        """Return station url."""
        return CidaUsgsWaterQuality.cql_filter_method()

    def get_measurements(self, well_data, harvester_well_data):
        """Get and save measurements."""
        pass
