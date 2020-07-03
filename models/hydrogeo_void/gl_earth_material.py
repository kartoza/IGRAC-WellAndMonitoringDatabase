from django.contrib.gis.db import models
from gwml2.models.universal import Quantity
from gwml2.models.hydrogeological_unit.gw_porosity import GWPorosity
from gwml2.models.fluid_body.gw_unit_fluid_property import GWUnitFluidProperty


class GWUnitVoidProperty(models.Model):
    """
    7.6.35 GW_UnitVoidProperty
    Properties inherent in the relation between a hydrogeological unit and a void:
    includes the proportion of voids to the unit (porosity)
    or to the connectivity / size of void openings (intrinsic permeability).

    """

    gw_permeability = models.ManyToManyField(
        Quantity, null=False, blank=False,
        verbose_name='gwPermeability',
        help_text="Refers to intrinsic permeability: "
                  "a measure of a material's ability to allow fluid flow "
                  "that is independent of fluid properties, and based on connectivity "
                  "of pores and size of their openings. This is not hydraulic conductivity."
    )
    gw_porosity = models.ManyToManyField(
        GWPorosity, null=False, blank=False,
        verbose_name='gwPorosity',
        help_text="Relates possibly many types of porosity values to a unit and related void combination.")


class GLEarthMaterial(models.Model):
    """
    7.6.3 GL_EarthMaterial
    Earth materials are substances,
    e.g. sandstone or granite, that constitute physical bodies, hydrogeological units.
    This class enables various hydrogeological properties
    to be attributed to a specific occurrence of a material,
    e.g. the sandstone of a specific aquifer.

    """

    gw_void_property = models.ForeignKey(
        GWUnitVoidProperty, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwVoidProperty',
        help_text="The porosity or permeability of a particular earth material that hosts a void.")
    gw_fluid_property = models.ForeignKey(
        GWUnitFluidProperty, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwFluidProperty',
        help_text="The hydraulic conductivity, transmissivity, or storativity of an earth material.")
