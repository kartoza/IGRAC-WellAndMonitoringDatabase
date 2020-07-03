from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm
from gwml2.models.hydrogeological_unit.gw_confining_bed import GWConfiningBed


class AquiferTypeTerm(GWTerm):
    """
    Water in an Aquifer is, or is not, under pressure.
    Based on that, several aquifer types can be
    distinguished: unconfined, confined, artesian,
    subartesian, or aquitard (after INSPIRE, 2013).
    """
    pass


class GWAquifer(models.Model):
    """
    7.6.5 GW_Aquifer
    A body of earth material that contains / potentially contains / potentially contained
    sufficient saturated permeable material to yield significant quantities of water to wells
    and springs (after Lohman, 1972).
    """
    gw_aquifer_type = models.ForeignKey(
        AquiferTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWAquiferType",
        help_text="Water in an Aquifer is, or is not, under pressure."
                  "Based on that, several aquifer types can be"
                  "distinguished: unconfined, confined, artesian,"
                  "subartesian, or aquitard (after INSPIRE, 2013)."
    )
    gw_aquifer_is_exploited = models.BooleanField(
        null=True, blank=True,
        verbose_name="GWAquiferIsExploited",
        help_text="Denotes whether groundwater from the "
                  "hydrogeological unit is being exploited by wells "
                  "or other intakes (after INSPIRE, 2013)."
    )
    gw_aquifer_is_main = models.BooleanField(
        null=True, blank=True,
        verbose_name="GWAquiferIsMain",
        help_text="Denotes whether the unit is primary in an"
                  "Aquifer System (after INSPIRE, 2013)."
    )

    gw_confining_bed = models.ManyToManyField(
        GWConfiningBed, null=True, blank=True,
        verbose_name="GWConfiningBed",
        help_text="Relates an aquifer and its confining beds."
    )
