from django.contrib.gis.db import models
from gwml2.models.flow.gw_discharge import GWDischarge
from gwml2.models.flow.gw_recharge import GWRecharge


class GWInterFlow(models.Model):
    """
    7.6.23 GW_InterFlow
    Fluid flow between features through an interface, exiting one feature and entering
    another. Features into which fluid is flowing are usually units, voids, or fluid bodies, but
    """
    gw_flow_location = models.MultiPointField(
        verbose_name="GWFlowLocation",
        help_text="The location at which water is being transferred from one feature into another."
    )

    # TODO:
    #  Not sure what Feature is
    # gw_flow_source_container = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowSourceContainer",
    #     help_text="The feature from which water is flowing."
    # )
    # gw_flow_source_body = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowSourceBody",
    #     help_text="The fluid body from which water is flowing."
    # )
    # gw_flow_destination_container = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowDestinationContainer",
    #     help_text="The feature into which water is flowing."
    # )
    # gw_flow_destination_body = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowDestinationBody",
    #     help_text="The fluid body into which water is flowing."
    # )
    # gw_flow_interface_feature = models.ManyToManyField(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowInterfaceFeature",
    #     help_text="The feature that denotes the interface between, "
    #               "for example, the groundwater and surface, "
    #               "such as a well, spring, seep, etc., or between two aquifers."
    # )

    gw_recharge = models.ManyToManyField(
        GWRecharge, null=True, blank=True,
        verbose_name="GWRecharge",
        help_text="Recharge is a type of interflow in which fluid enters a feature."
    )

    gw_discharge = models.ManyToManyField(
        GWDischarge, null=True, blank=True,
        verbose_name="GWDischarge",
        help_text="Discharge is a type of interflow in which fluid exits a feature."
    )
