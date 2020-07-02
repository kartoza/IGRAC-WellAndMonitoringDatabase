from django.contrib.gis.db import models
from gwml2.models.universal import Elevation, GWTerm
from gwml2.models.fluid_body.gw_fluid_body import GWFluidBody
from gwml2.models.well.gw_well import GWLicence


class GWStringType(GWTerm):
    """Type of spring e.g. mineral, thermal, saline, etc."""

    pass


class SpringCauseType(GWTerm):
    """The cause of the spring e.g. artesian, geyser, perched, etc."""

    pass


class SpringPersistenceType(GWTerm):
    """The periodicity of the spring e.g. ephemeral, perennial, intermittent, seasonal, etc."""

    pass


class GWSpring(models.Model):
    """
    7.6.32 GW_Spring
    Any natural feature where groundwater flows to the surface of the earth.

    """

    gw_spring_name = models.TextField(
        null=False, blank=False, verbose_name="gwSpringName",
        help_text="Name or ID of the spring."
    )
    gw_spring_location = models.GeometryField(
        null=True, blank=True, verbose_name="gwSpringLocation",
        help_text="Geometry / position of the spring."
    )
    gw_spring_reference_elevation = models.ManyToManyField(
        Elevation, null=False, blank=False,
        verbose_name="gwSpringReferenceElevation",
        help_text="Description of the accuracy of the elevation measurement.")
    gw_spring_type = models.ForeignKey(
        GWStringType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwSpringType",
        help_text="Type of spring e.g. mineral, thermal, saline, etc.")
    gw_spring_cause_type = models.ForeignKey(
        SpringCauseType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwSpringCauseType",
        help_text="Type of spring e.g. mineral, thermal, saline, etc.")
    gwSpringPersistence = models.ForeignKey(
        SpringPersistenceType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwSpringPersistence",
        help_text="The periodicity of the spring e.g. ephemeral, perennial, "
                  "intermittent, seasonal, etc.")

    # TODO: add this when we found GL_Feature
    # gw_spring_geology = models.ManyToManyField(
    #     GL_Feature, null=True, blank=True,
    #     verbose_name="gwSpringReferenceElevation",
    #     help_text="Related geology features.")

    # TODO: add this field when GW_Hydrogeounit is available
    # gwSpringUnit = models.ManyToManyField(
    #     GW_HydrogeoUnit, null=False, blank=False,
    #     verbose_name="gwSpringUnit",
    #     help_text="The hydrogeological unit(s) hosting the spring.")

    gw_spring_body = models.ManyToManyField(
        GWFluidBody, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwSpringBody",
        help_text="The fluid body being depleted by the spring.")

    gw_spring_construction = models.TextField(
        null=True, blank=True,
        verbose_name="gwSpringConstruction",
        help_text="Spring construction details, if any.")

    gw_spring_licence = models.ManyToManyField(
        GWLicence, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwSpringLicence",
        help_text="Any licence relating to the spring.")

    def __str__(self):
        return self.gw_spring_name
