from django.contrib.gis.db import models


class GWFlowSystem(models.Model):
    """
    7.6.17 GW_FlowSystem
    Flow path from recharge to discharge location, through hydrogeological units. It is
    related to a fluid body, and consists of a collection or aggregation of at least two specific
    flows, as well as possibly other flow systems.
    """
    gw_flow_path = models.GeometryField(
        verbose_name="GWFlowPath",
        help_text="The path of flow of a fluid through a container."
    )
    gw_part_of_system_flow = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="Relates a flow system part to a flow system whole.")
