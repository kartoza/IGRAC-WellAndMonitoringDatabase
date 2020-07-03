from django.contrib.gis.db import models
from gwml2.models.flow.gw_flow import GWFlow
from gwml2.models.fluid_body.gw_fluid_body_property import GWFluidBodyProperty
from gwml2.models.fluid_body.gw_fluid_body_surface import GWFluidBodySurface
from gwml2.models.fluid_body.gw_constituent import GWConstituent
from gwml2.models.fluid_body.gw_mixture import GWMixtureConstituent
from gwml2.models.universal import GWTerm, Quantity


class GWMetadata(models.Model):
    """Metadata for the unit.
    TODO: I couldn't find this specific model in the database, so we should find out more about this.
    """

    text = models.TextField(
        null=False, blank=False, verbose_name="GW_Metadata"
    )

    def __str__(self):
        return self.text


class BodyQualityType(GWTerm):
    """
    Categorical assessment of quality of the fluid body.
    """
    pass


class VulnerabilityType(GWTerm):
    """
    The type of vulnerability.
    """
    pass


class GWVulnerability(models.Model):
    """
    7.6.36 GW_Vulnerability
    The susceptibility of a feature to specific
    threats such as various physical events (earthquakes),
    human processes (depletion), etc.
    """

    gw_vulnerability_type = models.ForeignKey(
        VulnerabilityType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwVulnerabilityType",
        help_text="The type of vulnerability."
    )
    gw_vulnerability = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwVulnerability",
        help_text="A quantitative estimate of the susceptibility to contamination, "
                  "e.g. a DRASTIC value. "
                  "Should be accompanied by metadata about the method of calculation.",
        related_name='gw_vulnerability'
    )

    def __str__(self):
        return '{} - {}'.format(self.gw_vulnerability_type, self.gw_vulnerability)


class GWFluidBody(models.Model):
    """
    7.6.18 GW_FluidBody
    A distinct body of some fluid (liquid, gas) that fills
    the voids of a container such as an aquifer,
    system of aquifers, water well, etc.
    In hydrogeology this body is usually constituted by groundwater,
    but the model allows for other types of fillers e.g. petroleum.
    """

    gw_body_description = models.TextField(
        null=True, blank=True, verbose_name="gwBodyDescription",
        help_text="General description of the fluid body."
    )
    gw_body_metadata = models.ManyToManyField(
        GWMetadata, null=True, blank=True,
        verbose_name='gwBodyMetadata',
        help_text='Metadata for the unit.'
    )

    gw_body_flow = models.ManyToManyField(
        GWFlow, null=True, blank=True,
        verbose_name='gwBodyFlow',
        help_text='Flows associated with the fluid body.'
    )

    gw_body_quality = models.ManyToManyField(
        BodyQualityType, null=True, blank=True,
        verbose_name='gwBodyQuality',
        help_text='Categorical assessment of quality of the fluid body.'
    )
    gw_body_shape = models.GeometryField(
        null=True, blank=True, verbose_name="gwBodyShape",
        help_text="Shape and position of the fluid body."
    )
    gw_body_volume = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwBodyVolume",
        help_text="Description of the volume/quantity of a fluid present in a container at a certain time.",
        related_name='gw_body_volume'
    )
    gw_body_vulnerability = models.ManyToManyField(
        GWVulnerability, null=True, blank=True,
        verbose_name='gwBodyVulnerability',
        help_text='The susceptibility of the fluid body to specific threats such as surface contamination, etc.'
    )
    gw_part_of_body = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="Relates a void and a fluid body contained by.")
    gw_body_property = models.ManyToManyField(
        GWFluidBodyProperty, null=False, blank=False,
        verbose_name='gwBodyProperty',
        help_text='The property of fluid body.'
    )
    gw_body_surface = models.ManyToManyField(
        GWFluidBodySurface, null=False, blank=False,
        verbose_name='gwBodySurface',
        help_text='Relates a fluid body to a surface hosted by the body, e.g. the top of the water table.'
    )
    gw_body_constituent = models.ManyToManyField(
        GWMixtureConstituent, null=False, blank=False,
        verbose_name='gwBodyConstituent',
        help_text='Relates a fluid body to its chemical, biologic, or material constituents, '
                  'and specifies the nature of the mixture of the constituent within the body, '
                  'e.g. solution, suspension.'
    )
    gw_background_constituent = models.ManyToManyField(
        GWConstituent, null=False, blank=False,
        verbose_name='gwBackgroundConstituent',
        help_text='Relates a fluid body to typical background constituent values for that body.'
    )

    def __str__(self):
        return self.gw_body_description
