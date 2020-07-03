from django.contrib.gis.db import models
from gwml2.models.flow.gw_recharge import GWRecharge
from gwml2.models.flow.gw_discharge import GWDischarge
from gwml2.models.flow.gw_water_budget import GWWaterBudget
from gwml2.models.hydrogeological_unit.gw_porosity import PorosityTypeTerm
from gwml2.models.gw_unit_properties import GWUnitProperties
from gwml2.models.fluid_body.gw_fluid_body import GWVulnerability


class GWHydrogeoUnit(models.Model):
    """
    7.6.21 GW_HydrogeoUnit
    Any soil or rock unit or zone that by virtue of its hydraulic properties has a distinct
    influence on the storage or movement of groundwater (after ANS, 1980).
    """
    gw_unit_media = models.ForeignKey(
        PorosityTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWUnitMedia",
        help_text="Type of material or, by proximity, type of voids "
                  "(e.g. granular, fracture, karstic, or mixed)."
    )

    gw_unit_recharge = models.ManyToManyField(
        GWRecharge,
        verbose_name="GWUnitRecharge",
        help_text="Volumetric flow rate of water that enters an "
                  "hydrogeologic unit, at potentially multiple locations."
    )

    gw_unit_discharge = models.ManyToManyField(
        GWDischarge,
        verbose_name="GWUnitDischarge",
        help_text="Volumetric flow rate of water that goes out of an "
                  "hydrogeologic unit, at potentially multiple locations."
    )
    gw_unit_water_budget = models.ForeignKey(
        GWWaterBudget, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWUnitWaterBudget",
        help_text="Sum of water input and output of a "
                  "hydrogeologic unit, at a particular point in time, "
                  "with a description of inflows and outflows."
    )

    gw_unit_vulnerability = models.ManyToManyField(
        GWVulnerability, null=True, blank=True,
        verbose_name="gwUnitVulnerability",
        help_text="The susceptibility of the aquifer to specific "
                  "threats such as various physical events (earthquakes), "
                  "human processes (depletion), etc."
    )

    properties = models.ManyToManyField(
        GWUnitProperties, null=True, blank=True,
        verbose_name="Properties",
        help_text="Additional properties"
    )
