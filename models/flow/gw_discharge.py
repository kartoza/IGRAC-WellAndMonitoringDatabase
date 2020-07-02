from django.contrib.gis.db import models
from gwml2.models.universal import Quantity


class GWDischarge(models.Model):
    """
    7.6.14 GW_Discharge
    An outflow of fluid from a container such as an aquifer, watershed, pipe
    """
    flow_rate = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        verbose_name="FlowRateDischarge",
        help_text="Volumetric flow rate of water that goes out"
    )
