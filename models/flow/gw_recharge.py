from django.contrib.gis.db import models
from gwml2.models.universal import Quantity


class GWRecharge(models.Model):
    """
    7.6.31 GW_Recharge
    Fluid added to an aquifer by various means such as precipitation, injection, etc.
    """
    # TODO:
    #  Not sure what recharge data is
    #  just add flow_rate because of definition
    flow_rate = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        verbose_name="FlowRateRecharge",
        help_text="Volumetric flow rate of water that enters"
    )
