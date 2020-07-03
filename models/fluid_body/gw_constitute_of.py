from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm


class ConstituentRelationType(GWTerm):
    """
    Specific type of relation between fluid body components,
    e.g. coating, constitution, aggregation, containment.

    """

    pass


class MechanismType(GWTerm):
    """Mechanisms by which materials (of various states) come into a relationship,
    e.g. sorption, precipitation, digestion, excretion, etc.

    """

    pass


class GWConstituentRelation(models.Model):
    """
    7.6.13 GW_ConstituentRelation
    Relation between fluid body components, typically caused by a specific mechanism,
    e.g. coating (from adsorption), constitution (from chemical bonding forming a new material),
    aggregation (from physical bonding, e.g. pressure), containment (from absorption, digestion).

    """

    gw_constituent_relation_type = models.ForeignKey(
        ConstituentRelationType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwConstituentRelationType',
        help_text="Specific type of relation between fluid body components, "
                  "e.g. coating, constitution, aggregation, containment.")
    gw_constitution_relation_mechanism = models.ForeignKey(
        MechanismType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='gwConstitutionRelationMechanism',
        help_text="Mechanisms by which materials (of various states) come into a relationship, "
                  "e.g. sorption, precipitation, digestion, excretion, etc.")


class GWConstituteOf(models.Model):
    """A general binary relation between constituents,
    in which the relation type can be specified in addition
    to the causal mechanism that caused the relationship.

    """

    gw_constituent_relation = models.ForeignKey(
        GWConstituentRelation, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='GWConstituentRelation',
        help_text="Relation between fluid body components, "
                  "typically caused by a specific mechanism.")
    gw_constituent = models.ForeignKey(
        'gwml2.GWConstituent', null=False, blank=False,
        on_delete=models.CASCADE,
        verbose_name='GWConstituent',
    )
