from django.contrib.gis.db import models
from gwml2.models.universal import Elevation, GWTerm


class SiteType(GWTerm):
    """Type of monitoring site, e.g. well, gauging station, etc."""

    pass


class GWMonitoringSite(models.Model):
    """
    7.6.29 GW_MonitoringSite
    Site of observation related to groundwater.
    """

    gw_site_name = models.TextField(
        null=True, blank=True, verbose_name="gwSiteName",
        help_text="Name (or identifier) of the monitoring site.")
    gw_site_location = models.PointField(
        null=False, blank=False, verbose_name="gwSiteLocation",
        help_text="Spatial location of the site.")
    gw_site_reference_elevation = models.ManyToManyField(
        Elevation, null=False, blank=False,
        verbose_name='gwSiteReferenceElevation',
        help_text='Reference elevation for all observations at the site, '
                  'e.g. ground elevation, casing elevation. '
                  'This can differ from the host feature elevation, or be more specific.')
    gw_site_type = models.ForeignKey(
        SiteType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwSiteType',
        help_text="Type of monitoring site, e.g. well, gauging station, etc.")

    # TODO: uncomment this when we have Feature class available
    # gwMonitoringHost = models.ForeignKey(
    #     Feature, null=False, blank=False,
    #     on_delete=models.SET_NULL, verbose_name='gwMonitoringHost',
    #     help_text="The feature hosting the site, e.g. a well, spring, lake or stream.")

    def __str__(self):
        return self.gw_site_name
