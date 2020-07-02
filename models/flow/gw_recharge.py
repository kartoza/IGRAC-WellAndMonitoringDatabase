from django.contrib.gis.db import models
from gwml2.models.universal import Quantity


class GWRecharge(models.Model):
    """
    7.6.31 GW_Recharge
    Fluid added to an aquifer by various means such as precipitation, injection, etc.
    """
    flow_rate = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        verbose_name="FlowRateRecharge",
        help_text="Volumetric flow rate of water that enters"
    )
