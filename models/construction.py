from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from gwml2.models.general import Quantity
from gwml2.models.term import (
    TermConstructionStructureType, TermReferenceElevationType)


class Construction(models.Model):
    """ Construction
    """
    pump_installer = models.CharField(
        _('Pump installer'),
        null=True, blank=True, max_length=200,
        help_text=_("Name of the company or person who installed the pump.")
    )
    pump_description = models.TextField(
        _('Pump description'),
        null=True,
        blank=True,
        help_text=_("Any relevant information on the pump (e.g. model, capacity, energy supply, depth).")
    )

    class Meta:
        db_table = 'construction'


class ConstructionStructure(models.Model):
    """
    Structure of construction
    """
    construction = models.ForeignKey(
        Construction, on_delete=models.CASCADE,
        null=True, blank=True
    )
    type = models.ForeignKey(
        TermConstructionStructureType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Type')
    )
    reference_elevation = models.ForeignKey(
        TermReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Reference elevation')
    )

    # information
    material = models.CharField(
        _('Material'),
        null=True, blank=True, max_length=200
    )
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True)

    # position
    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='structure_top_depth',
        verbose_name=_('Top depth')
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='structure_bottom_depth',
        verbose_name=_('Bottom depth')
    )
    diameter = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='structure_diameter',
        verbose_name=_('Diameter')
    )

    class Meta:
        ordering = ('top_depth__value',)
        db_table = 'construction_structure'
