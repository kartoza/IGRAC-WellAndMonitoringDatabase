from django.contrib.gis.db import models


class GWIntraFlow(models.Model):
    """
    7.6.24 GW_IntraFlow
    Fluid flow within a feature such as a unit, void, gw body, or even a man-made feature
    such as a conduit of some kind.
    """
    gw_flow_location = models.MultiPointField(
        verbose_name="GwFlowLocation",
        help_text="The location where a fluid is flowing within a feature."
    )

    # TODO:
    #  Not sure what Feature is
    # gw_flow_container = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowContainer",
    #     help_text="The feature in which the fluid is flowing. "
    #               "Typically a unit, void, or gw body, but can also "
    #               "be a man made feature such as some conduit."
    # )
    # gw_flow_body = models.ForeignKey(
    #     Feature, null=True, blank=True,
    #     on_delete=models.SET_NULL,
    #     verbose_name="GWFlowBody",
    #     help_text="The fluid body that is flowing."
    # )
