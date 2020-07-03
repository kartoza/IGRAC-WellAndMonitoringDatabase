from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm, Quantity


class PorosityTypeTerm(GWTerm):
    """
    Type of porosity (primary, secondary, dual,
    specific, effective, granular, fractured, karstic,
    etc.)
    """
    pass


class GWPorosity(models.Model):
    """
    7.6.30 GW_Porosity
    Measure of the proportion of the volume occupied by specific voids over the total volume
    of material including the voids. Voids are differentiated from 'porosity' in that porosity is
    a proportion, while voids are the spaces themselves. Types of porosity include: primary,
    secondary, dual, specific, effective, granular, fractured, karstic, etc.
    """

    gw_porosity_type = models.ForeignKey(
        PorosityTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWPorosityType",
        help_text="Type of porosity (primary, secondary, dual, "
                  "specific, effective, granular, fractured, karstic, etc.)"
    )

    gw_porosity = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWPorosity",
        help_text="Measure of the proportion of the volume "
                  "occupied by specific voids over the total "
                  "volume of material including the voids."
    )
