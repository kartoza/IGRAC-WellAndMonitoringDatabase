from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm, Quantity
from gwml2.models.flow.gw_flow_system import GWFlowSystem


class WaterFlowProcess(GWTerm):
    """
    The process causing the flow, e.g.
    evapotranspiration, evaporation, transpiration, runoff,
    baseflow, pumping, infiltration, injection, etc.
    """
    pass


class FlowPersistenceType(GWTerm):
    """
    The regularity of flow occurrence, e.g.
    ephemeral, intermittent, perennial, seasonal.
    After
    http://inspire.ec.europa.eu/codeList/WaterPersist
    enceValue/ (INSPIRE, 2013).
    """
    pass


class GWFlow(models.Model):
    """
    7.6.16 GW_Flow
    Process by which the fluid enters or exits a hydrogeological unit or a void, or flows
    within a unit or a void. Can flow from/to other natural or man-made features such as
    rivers, filtration stations, etc.
    """
    gw_flow_system = models.ForeignKey(
        GWFlowSystem, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWFlowSystem",
        help_text="Relates a flow system to the individual flows"
                  "that comprise the system. "
                  "Flows are atomic entities that cannot have parts, "
                  "but which form parts of flow systems"
    )

    gw_flow_process = models.ForeignKey(
        WaterFlowProcess, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWFlowProcess",
        help_text="The process causing the flow, e.g. "
                  "evapotranspiration, evaporation, transpiration, runoff, "
                  "baseflow, pumping, infiltration, injection, etc."
    )
    gw_flow_time = models.TextField(
        null=True, blank=True,
        verbose_name="GWFlowTime",
        help_text="Refers to the duration, instant or interval of the flow "
                  "(actual time, not observation time). "
                  "E.g. \"yearly\", \"summer\", \"2009\" or \"2009-2011\"."
    )
    gw_flow_velocity = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='gw_flow_velocity',
        on_delete=models.SET_NULL,
        verbose_name="GWFlowVelocity",
        help_text="Measure of water volume per unit of time."
    )
    gw_flow_volume_rate = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='gw_flow_volume_rate',
        on_delete=models.SET_NULL,
        verbose_name="GWFlowVolumeRate",
        help_text="Measure of water quantity per time period with uom."
    )
    gw_flow_persistence = models.ForeignKey(
        FlowPersistenceType, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwFlowPersistence",
        help_text="The regularity of flow occurrence, "
                  "e.g. ephemeral, intermittent, perennial, seasonal. "
                  "After http://inspire.ec.europa.eu/codeList/WaterPersist enceValue/ (INSPIRE, 2013)."
    )
