from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm, Quantity


class GWBodyPropertyType(GWTerm):
    """Categorical assessment of quality of the fluid body as a whole:
    e.g. saline, brackish, fresh, turbide, sulfurous, mixed, ... 1000-3000mg/l tds, etc.
    A normative quality description is an assessment based upon some guideline
    edited by a government or a quality standard.

    """

    pass


class GWFluidBodyProperty(models.Model):
    """
    7.6.19 GW_FluidBodyProperty
    Additional properties that characterize a fluid body.
    Can include synoptic values for the whole body or location-specific observations such as
    age, temperature, density, viscosity, turbidity, color, hardness, acidity, etc.

    """

    gw_body_property = models.ForeignKey(
        GWBodyPropertyType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwBodyProperty',
        help_text="Type of fluid body property, "
                  "e.g. age, temperature, density, viscosity, turbidity, color, hardness, acidity, etc..")
    gw_body_property_value = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwBodyPropertyValue',
        help_text="Value of the fluid body property (with uom).")

    def __str__(self):
        return self.gw_body_property

