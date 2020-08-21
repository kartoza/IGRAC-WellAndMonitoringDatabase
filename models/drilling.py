from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.models.term import TermDrillingMethod


class Drilling(models.Model):
    """ Drilling
    """
    reference_elevation = models.OneToOneField(
        ReferenceElevation, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    total_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Total depth of stratigraphic'
    )
    drilling_method = models.ForeignKey(
        TermDrillingMethod, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    driller = models.CharField(
        null=True, blank=True, max_length=512)
    successful = models.BooleanField(
        null=True,
        blank=True)
    failed_explanation = models.TextField(
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
    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the log',
        related_name='stratigraphic_log_top_depth'
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the log',
        related_name='stratigraphic_log_bottom_depth'
    )
    material = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="Material of the log."
    )
    stratigraphic_unit = models.CharField(
        null=True, blank=True, max_length=256,
        help_text="Stratigraphic unit of the log."
    )

    class Meta:
        db_table = 'drilling_stratigraphic_log'


class WaterStrike(models.Model):
    """ Water strike
    """
    drilling = models.ForeignKey(
        Drilling, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of feature'
    )
    description = models.TextField(
        null=True,
        blank=True)

    class Meta:
        db_table = 'drilling_water_strike'
