from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm


class UnitPropertyTerm(GWTerm):
    """
    The type of vulnerability.
    """
    pass


class GWUnitProperties(models.Model):
    """
    7.6.34 GW_UnitProperties
    Additional properties of an aquifer not included in the model.
    """

    gw_unit_property = models.ForeignKey(
        UnitPropertyTerm,
        on_delete=models.CASCADE,
        verbose_name="gwUnitProperty",
        help_text="The type of hydrogeological unit property, e.g. average well depth."
    )

    gw_unit_property_value = models.TextField(
        verbose_name="gwUnitPropertyValue",
        help_text="The value of the hydrogeological unit property."
    )
