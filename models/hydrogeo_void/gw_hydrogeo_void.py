from django.contrib.gis.db import models
from gwml2.models.hydrogeological_unit.gw_hydrogeo_unit import GWHydrogeoUnit
from gwml2.models.hydrogeo_void.gl_earth_material import GLEarthMaterial, GWUnitVoidProperty
from gwml2.models.fluid_body.gw_fluid_body import GWMetadata, GWFluidBody
from gwml2.models.hydrogeological_unit.gw_porosity import PorosityTypeTerm
from gwml2.models.universal import Quantity


class GWVoidUnit(models.Model):
    """Model to connect GW_HydrogeoUnit and GW_UnitVoidProperty"""

    gw_hydrogeo_unit = models.ForeignKey(
        GWHydrogeoUnit, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='GWHydrogeoUnit')
    gw_unit_void_property = models.ForeignKey(
        GWUnitVoidProperty, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='GWUnitVoidProperty')


class GWHydrogeoVoid(models.Model):
    """
    7.6.22 GW_HydrogeoVoid
    Voids represent the spaces inside (hosted by) a unit or its material.
    E.g. the pores in an aquifer, or in the sandstone of an aquifer.
    Voids can contain fluid bodies.
    Voids are differentiated from 'porosity' in that porosity is the proportion of
    void volume to total volume, while voids are the spaces themselves.
    Voids are required in GWML2, for example,
    to capture the volume of fractures in an aquifer.

    """

    gw_void_description = models.TextField(
        null=True, blank=True, verbose_name="gwVoidDescription",
        help_text="General description of the void.")
    gw_void_host_material = models.ManyToManyField(
        GLEarthMaterial, null=True, blank=True,
        verbose_name='gwVoidHostMaterial',
        help_text="The material that hosts the void, if specified. "
                  "Note voids can be hosted by a unit (an aquifer) or its material (e.g. sandstone)."
    )
    gw_void_metadata = models.ForeignKey(
        GWMetadata, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwVoidMetadata',
        help_text='Metadata for the void.'
    )
    gw_void_shape = models.GeometryField(
        null=True, blank=True, verbose_name="gwVoidShape",
        help_text="Shape and position of the void."
    )
    gw_void_type = models.ForeignKey(
        PorosityTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwVoidType',
        help_text="Type of void e.g. fractured, intergranular, etc.")
    gw_void_volume = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwVoidVolume',
        help_text="Volume of the void.")
    gw_part_of_void = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwPartOfVoid',
        help_text="Relates a void and a fluid body contained by.")
    gw_fluid_body_void = models.ForeignKey(
        GWFluidBody, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwFluidBodyVoid',
        help_text="Each void contains at most one fluid body, "
                  "which can have multiple parts that could be disconnected.")
    gw_void_unit = models.ManyToManyField(
        GWVoidUnit, null=True, blank=True,
        verbose_name='gwVoidUnit',
        help_text="Relates hydrogeological units with a void hosted by the units.")

    def __str__(self):
        return self.gw_void_description
