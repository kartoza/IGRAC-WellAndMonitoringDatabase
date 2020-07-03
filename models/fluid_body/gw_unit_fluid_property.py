from django.contrib.gis.db import models
from gwml2.models.universal import Quantity
from gwml2.models.fluid_body.gw_yield import GWYield


class GWUnitFluidProperty(models.Model):
    """
    7.6.33 GW_UnitFluidProperty
    A measured or calculated physical or hydraulic property
    that can be inherent in either an aquifer or its material,
    and some fluid body, e.g. hydraulic conductivity, transmissivity, storativity, permeability, porosity.

    """

    gw_hydraulic_conductivity = models.ManyToManyField(
        Quantity, null=False, blank=False,
        verbose_name='gwHydraulicConductivity',
        help_text="Hydraulic conductivity measures how easily a fluid can move through the voids in a material."
    )
    gw_transmissivity = models.ManyToManyField(
        Quantity, null=False, blank=False,
        verbose_name='gwTransmissivity',
        help_text="The rate of groundwater flow laterally through an aquifer, "
                  "determined by hydraulic conductivity and container thickness.",
        related_name='gw_transmissivity'
    )
    gw_storativity = models.ManyToManyField(
        Quantity, null=False, blank=False,
        verbose_name='gwStorativity',
        help_text="Storativity is the volume of water released from storage per unit "
                  "decline in hydraulic head in the aquifer, per unit area of the aquifer.",
        related_name='gw_storativity'
    )
    gw_yield = models.ManyToManyField(
        GWYield, null=False, blank=False,
        verbose_name='gwYield',
        help_text="Relates possibly many types of yield values to a unit and fluid body combination."
    )
