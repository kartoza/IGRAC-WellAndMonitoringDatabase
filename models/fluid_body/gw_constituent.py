from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm, Quantity
from gwml2.models.fluid_body.gw_constitute_of import GWConstituteOf


class StateType(GWTerm):
    """
    The physical state of the constituent, i.e. solid, liquid, or gas.

    """

    pass


class MaterialType(GWTerm):
    """Material component type."""

    pass


class ChemicalType(GWTerm):
    """Chemical component type."""

    pass


class OrganismType(GWTerm):
    """Biological species."""

    pass


class GWMaterialConstituent(models.Model):
    """
    7.6.27 GW_MaterialConstituent
    Suspended or colloidal material in a fluid body, e.g., sediment.

    """

    gw_material = models.ForeignKey(
        MaterialType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwMaterial',
        help_text="Name of the suspended or colloid material in the fluid body, e.g. a lithology or mineral name.")

    def __str__(self):
        return self.gw_material


class GWChemicalConstituent(models.Model):
    """
    7.6.10 GW_ChemicalConstituent
    Characterization of the chemical composition of the fluid body, both natural and man-made.
    """

    gw_chemical = models.ForeignKey(
        ChemicalType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwChemical',
        help_text="Chemical component type, e.g. arsenic.")

    def __str__(self):
        return self.gw_chemical


class GWBiologicConstituent(models.Model):
    """
    7.6.9 GW_BiologicConstituent
    Characterization of the biological composition of the fluid body, both natural and man-made.

    """

    gw_organism = models.ForeignKey(
        OrganismType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwOrganism',
        help_text="Biological species.")
    gw_state = models.ForeignKey(
        StateType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwState',
        help_text="Organisms are always solids.")

    def __str__(self):
        return self.gw_organism


class GWConstituent(models.Model):
    """
    7.6.12 GW_Constituent
    General (abstract) entity denoting a material, chemical or biological constituent of a fluid body.
    """

    gw_concentration = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwConcentration",
        help_text="The concentration (with uom) of the constituent in the fluid body.",
        related_name='gw_concentration'
    )
    gw_state = models.ForeignKey(
        StateType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwState',
        help_text="The physical state of the constituent, i.e. solid, liquid, or gas.")
    gw_constitute_of = models.ForeignKey(
        GWConstituteOf, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='GWConstituteOf',
        help_text="A general binary relation between constituents, "
                  "in which the relation type can be specified in addition to the causal "
                  "mechanism that caused the relationship.")
    gw_material_constituent = models.ForeignKey(
        GWMaterialConstituent, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='GWMaterialConstituent',
        help_text="A material constituent is a type of fluid body constituent, e.g. sediment.")
    gw_chemical_constituent = models.ForeignKey(
        GWChemicalConstituent, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='GWChemicalConstituent',
        help_text="A chemical constituent is a type of fluid body constituent, e.g. arsenic.")
    gw_biologic_constituent = models.ForeignKey(
        GWBiologicConstituent, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='GWBiologicConstituent',
        help_text="A biologic constituent is a type of fluid body constituent, e.g. organisms.")
