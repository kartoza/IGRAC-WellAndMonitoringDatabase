from django.contrib.gis.db import models
from gwml2.models.flow.gw_flow_system import GWFlowSystem


class GWDivide(models.Model):
    """
    7.6.15 GW_Divide
    “A line on a water table or piezometric surface, on either side of which the groundwater
    flow diverges" (IGH0556).
    """

    gw_divide_shape = models.GeometryField(
        verbose_name="GWDivideShape",
        help_text="Shape / position of the divide (line, plane or point) "
                  "intersecting a fluid body surface."
    )

    gw_flow_system = models.ManyToManyField(
        GWFlowSystem,
        verbose_name="GWFlowSystem",
        help_text="Flow system on each side of the divide."
    )
