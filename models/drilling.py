from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermDrillingMethod, TermReferenceElevationType
from django.utils.translation import gettext_lazy as _


class Drilling(models.Model):
    """ Drilling
    """
    drilling_method = models.ForeignKey(
        TermDrillingMethod, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Excavation method')
    )
    driller = models.CharField(
        _('Contractor'),
        null=True, blank=True, max_length=512,
        help_text=_('Name of the drilling company or responsible person.'))
    successful = models.BooleanField(
        _('Successful'),
        null=True,
        blank=True)
    cause_of_failure = models.TextField(
        _('Cause of failure'),
        null=True,
        blank=True,
        help_text=_('Explain why the drilling was not successful.'))
    year_of_drilling = models.PositiveIntegerField(
        _('Construction year'),
        null=True,
        blank=True)

    class Meta:
        db_table = 'drilling'


class StratigraphicLog(models.Model):
    """
    8.1.9 GW_stratigraphicLog
    Specialization of the OM_Observation containing the log start and end depth for
    coverages.
    For Stratigraphic logs the observedProperty will be a GeoSciML:GeologicUnit/name.
    For Lithologic logs the observedProperty will be a
    GeoSciML:GeologicUnit/composition/CompositionPart/material.
    """
    drilling = models.ForeignKey(
        Drilling, on_delete=models.CASCADE,
    )

    # Log information
    reference_elevation = models.ForeignKey(
        TermReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Reference elevation')
    )
    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stratigraphic_log_top_depth',
        verbose_name=_('Top depth')
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stratigraphic_log_bottom_depth',
        verbose_name=_('Bottom depth')
    )
    material = models.CharField(
        _('Material'),
        null=True, blank=True, max_length=200
    )
    stratigraphic_unit = models.CharField(
        _('Stratigraphic unit'),
        null=True, blank=True, max_length=128
    )

    class Meta:
        ordering = ('top_depth__value',)
        db_table = 'drilling_stratigraphic_log'


class WaterStrike(models.Model):
    """ Water strike
    """
    drilling = models.ForeignKey(
        Drilling, on_delete=models.CASCADE,
        null=True, blank=True
    )

    # information
    reference_elevation = models.ForeignKey(
        TermReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Reference elevation')
    )
    depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Depth')
    )
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True)

    class Meta:
        db_table = 'drilling_water_strike'
