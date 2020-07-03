from django.contrib.gis.db import models
from gwml2.models.universal import Quantity, GWTerm


class YieldType(GWTerm):
    """
    Type of porosity (primary, secondary, dual,
    specific, effective, granular, fractured, karstic,
    etc.)
    """
    pass


class GWYield(models.Model):
    """
    7.6.39 GW_Yield
    Yield is the rate of fluid withdrawal associated with a unit, well, etc., expressed as m 3 .
    There are several types of yield, that can be considered: specific yield, sustainable yield,
    safe yield, aquifer yield, etc.
    """
    gw_yield_type = models.ForeignKey(
        YieldType, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwYieldType",
        help_text="Type of aquifer yields: e.g. specific yield, safe yield, etc."
    )

    gw_yield = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwYield",
        help_text="Measurement of the yield in units of volume per unit of time."
    )
