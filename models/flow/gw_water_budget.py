from django.contrib.gis.db import models
from gwml2.models.flow.gw_recharge import GWRecharge
from gwml2.models.flow.gw_discharge import GWDischarge
from gwml2.models.universal import Quantity


class GWWaterBudget(models.Model):
    """
    7.6.37 GW_WaterBudget
    An accounting of the water input and output of a hydrogeological unit, at a particular
    point in time, with a description of inflows and outflows.
    """
    gw_budget_amount = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWBudgetAmount",
        help_text="Final quantity (sum) of the budget. If recharge ="
                  "discharge, the sum is 0."
    )

    gw_budget_valid_time = models.DateTimeField(
        null=True, blank=True,
        verbose_name='GWBudgetValidTime',
        help_text='Valid time of this budget (e.g., 2010).'
    )

    gw_budget_recharge = models.ManyToManyField(
        GWRecharge,
        verbose_name="GWBudgetRecharge",
        help_text="Recharge (inflows) considered by the budget."
    )

    gw_budget_discharge = models.ManyToManyField(
        GWDischarge,
        verbose_name="GWBudgetDischarge",
        help_text="Discharge (outflows) considered in the budget."
    )
