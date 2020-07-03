from django.contrib.gis.db import models
from gwml2.models.hydrogeological_unit.gw_aquifer import GWAquifer
from gwml2.models.hydrogeological_unit.gw_aquifer_system import GWAquiferSystem
from gwml2.models.hydrogeological_unit.gw_confining_bed import GWConfiningBed


class GWAquiferUnit(models.Model):
    """
    7.6.7 GW_AquiferUnit
    Denotes aquifer-related hydrogeological units:
    aquifer systems, aquifers, or confining beds.
    """

    gw_aquifer = models.ForeignKey(
        GWAquifer, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWAquifer",
        help_text="An aquifer is a type of aquifer-related unit."
    )

    gw_aquifer_system = models.ManyToManyField(
        GWAquiferSystem, null=True, blank=True,
        verbose_name="GWAquiferSystem",
        help_text="An aquifer system is a type of aquifer-related unit."
    )

    gw_confining_bed = models.ForeignKey(
        GWConfiningBed, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWConfiningBed",
        help_text="A confining bed is a type of aquifer-related unit."
    )
