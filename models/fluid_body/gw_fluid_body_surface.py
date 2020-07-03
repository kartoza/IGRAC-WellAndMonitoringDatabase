from django.contrib.gis.db import models
from gwml2.models.flow.gw_divide import GWDivide
from gwml2.models.observations_measurements import OMObservation
from gwml2.models.universal import GWTerm


class SurfaceType(GWTerm):
    """Type of fluid body surface, e.g. piezometric,
    potentiometric, water table, salt wedge, etc.

    """

    pass


class GWFluidBodySurface(models.Model):
    """
    7.6.20 GW_FluidBodySurface
    A surface on a fluid body within a local or regional area,
    e.g. piezometric, potentiometric, water table, salt wedge, etc.

    """

    gw_surface_shape = models.GeometryField(
        null=True, blank=True, verbose_name="gwSurfaceShape",
        help_text="Geometry / position of the surface."
    )
    gw_surface_type = models.ForeignKey(
        SurfaceType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwSurfaceType',
        help_text="Type of fluid body property, "
                  "e.g. age, temperature, density, viscosity, "
                  "turbidity, color, hardness, acidity, etc..")
    gw_surface_metadata = models.ForeignKey(
        OMObservation, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwSurfaceMetadata',
        help_text="The observation or calculation of the surface.")
    gw_surface_divide = models.ManyToManyField(
        GWDivide, null=True, blank=True,
        verbose_name='gwSurfaceDivide',
        help_text='Relates a fluid body surface to a line on '
                  'e.g. a water table or piezometric surface, '
                  'on either side of which the groundwater flow diverges.'
    )
