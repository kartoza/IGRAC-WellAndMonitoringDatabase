from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm
from gwml2.models.contact_information import CIResponsibleParty
from gwml2.models.flow.gw_water_budget import GWWaterBudget
from gwml2.models.time import TMPeriod
from gwml2.models.fluid_body.gw_fluid_body import GWFluidBody
from gwml2.models.fluid_body.gw_yield import GWYield
from gwml2.models.hydrogeological_unit.gw_hydrogeo_unit import GWHydrogeoUnit
from gwml2.models.universal import DocumentCitation


class ManagementAreaTypeTerm(GWTerm):
    """
    General classification of the management area
    (e.g. restricted use zone, irrigation area,
    consumption area, etc.)
    """
    pass


class SpecialisedZoneAreaTypeTerm(GWTerm):
    """
    Additional classification value which further
    specialises the gwAreaType.
    """
    pass


class EnvironmentalDomainTypeTerm(GWTerm):
    """
    Classification of the environment domain(s) for
    which, through the establishment of the
    management area, certain environmental
    objectives are to be reached.
    """
    pass


class GWManagementArea(models.Model):
    """
    7.6.26 GW_ManagementArea
    The GW_ManagementArea represents an area of ground identified for management
    purposes. The area can be delineated by human factors such as policy or regulation
    concerns, as well as by domain concerns (in this case hydrogeological or hydrological).
    The spatial boundaries of a management area do not necessarily align exactly with
    associated hydrogeological feature boundaries. GW_ManagementArea has the potential
    to provide a pattern for a more generic OGC 'trans-domain' feature management class.
    GW_ManagementArea is equivalent to
    InspireAM:ManagementRestrictionOrRegulationZone.
    """

    gw_area_name = models.TextField(
        verbose_name="gwAreaName",
        help_text="Name of the management area."
    )
    gw_area_description = models.TextField(
        verbose_name="gwAreaDescription",
        help_text="General description of the management area."
    )

    # TODO:
    #  Not sure what Feature is
    # gw_area_feature = models.ManyToManyField(
    #     Feature,
    #     verbose_name="gwAreaFeature",
    #     help_text="Other features that are associated with the "
    #               "management area (watershed, ecological zones, etc) "
    #               "that are not hydrogeological units."
    # )

    gw_area_water_budget = models.ManyToManyField(
        GWWaterBudget,
        verbose_name="gwAreaWaterBudget",
        help_text="Water budget associated with the management area."
    )

    gw_area_yield = models.ForeignKey(
        GWYield, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwAreaYield',
        help_text='Yield associated with the management area.')

    gw_area_shape = models.GeometryField(
        verbose_name='gwAreaShape',
        help_text='Geometric shape and position of management area.')

    gw_area_type = models.ForeignKey(
        ManagementAreaTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwAreaType',
        help_text='General classification of the management area'
                  '(e.g. restricted use zone, irrigation area,'
                  'consumption area, etc.)')

    gw_area_specialised_area_type = models.ForeignKey(
        SpecialisedZoneAreaTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwAreaSpecialisedAreaType',
        help_text='Additional classification value which further'
                  'specialises the gwAreaType.')

    gw_area_environmental_domain = models.ForeignKey(
        EnvironmentalDomainTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwAreaEnvironmentalDomain',
        help_text='Classification of the environment domain(s) for '
                  'which, through the establishment of the '
                  'management area, certain environmental '
                  'objectives are to be reached.')

    gw_area_competent_authority = models.ManyToManyField(
        CIResponsibleParty, null=True, blank=True,
        verbose_name='gwAreaCompetentAuthority',
        help_text='Description of the organization(s) responsible for'
                  'managing, restricting or regulating measures or'
                  'activities within the management area.')

    gw_area_designation_period = models.ForeignKey(
        TMPeriod, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='gwAreaDesignationPeriod',
        help_text='Time period specifying when the management '
                  'area was legally designated or became effective in the real world.')

    gw_area_body = models.ManyToManyField(
        GWFluidBody, null=False, blank=False,
        verbose_name='gwAreaBody',
        help_text='Relates a management area to the fluid bodies contained within the'
                  'area. As with units, the spatial boundaries of management areas do'
                  'not necessarily coincide with the spatial boundaries of fluid bodies.'
    )

    gw_managed_unit = models.ManyToManyField(
        GWHydrogeoUnit, null=False, blank=False,
        verbose_name='gwManagedUnit',
        help_text='Relates a management area to the hydrogeological units contained within it.'
                  'Because the spatial boundaries of management areas can be determined by '
                  'human concerns, e.g. regulatory, these boundaries do not necessarily align with '
                  'the spatial boundaries of units, which are determined by physical criteria.'
    )

    related_management_area = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='relatedManagementArea',
        help_text='Relates a management area part to a management area whole.')

    documentation = models.ForeignKey(
        DocumentCitation, null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text='Relates legislative and reference documentation to a management area.')
