from django.contrib.gis.db import models
from groundwater.models.well_construction import Borehole
from groundwater.models import GWTerm, Quantity


class WellStatusTypeTerm(GWTerm):
    """
    Status of the well, Can be new, unfinished,
    reconditioned, deepened, not in use, standby,
    unknown, abandoned dry, abandoned
    insufficient, abandoned quality. (gwml1)
    """
    pass


class GWLicence(models.Model):
    """
    7.6.25 GW_Licence
    Licence relating to the drilling of a well, the extraction of groundwater, etc.
    """

    gw_licence_id = models.CharField(
        max_length=150,
        verbose_name='gwLicenceID',
        help_text='Licence ID, e.g. a number.')
    gw_purpose = models.TextField(
        null=False, blank=False, verbose_name="gwPurpose",
        help_text="Role of the licence.")
    gw_associated_gw_volume = models.FloatField(
        null=True, blank=True,
        verbose_name='gwAssociatedGWVolume',
        help_text='Fluid volume associated with the licence.'
    )
    gw_time_period = models.DateTimeField(
        null=True, blank=True, verbose_name='gwTimePeriod',
        help_text='The period of time for which the licence is valid.'
    )


class GWWell(models.Model):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""

    gw_well_name = models.TextField(
        null=False, blank=False, verbose_name="gwWellName",
        help_text="Name or ID of the well.")
    gw_well_location = models.PointField(
        null=False, blank=False, verbose_name="gwWellLocation",
        help_text="Surface location of the well.")
    gw_well_contribution_zone = models.GeometryField(
        null=True, blank=True, verbose_name="gwWellContributionZone",
        help_text="The area or volume surrounding a pumping well"
                  "or other discharge site that encompasses all areas"
                  "and features that supply groundwater to the well"
                  "or discharge site.")
    gw_well_construction = models.ForeignKey(
        Borehole, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellConstruction",
        help_text="Construction details for a well.")
    gw_well_total_length = models.FloatField(
        null=True, blank=True,
        verbose_name="gwWellTotalLength",
        help_text="Total length of the well from reference elevation.")
    gw_well_status = models.ForeignKey(
        WellStatusTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStatus",
        help_text="Status of the well, Can be new, unfinished, "
                  "reconditioned, deepened, not in use, standby,"
                  "unknown, abandoned dry, abandoned"
                  "insufficient, abandoned quality. (gwml1)")
    gw_well_static_water_depth = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStaticWaterDepth",
        help_text="Depth of the fluid body (e.g. piezometric level).",
        related_name='gw_well_static_water_depth'
    )
    gw_well_licence = models.OneToOneField(
        GWLicence, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwWellLicence',
        help_text='Licence relating to the drilling of the well or to the extraction of groundwater.'
    )
    gw_well_constructed_depth = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellConstructedDepth",
        help_text="Constructed depth of the well.",
        related_name='gw_well_constructed_depth'
    )
