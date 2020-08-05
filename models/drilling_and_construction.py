from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermDrillingMethod


class DrillingAndConstruction(models.Model):
    """ Drilling and Construction
    """
    drilling_method = models.ForeignKey(
        TermDrillingMethod, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    driller = models.CharField(
        null=True, blank=True, max_length=512)
    successful = models.BooleanField(
        null=True,
        blank=True)
    pump_installer = models.CharField(
        null=True, blank=True, max_length=512)
    pump_description = models.TextField(
        null=True,
        blank=True)


class WaterStrike(models.Model):
    """ Water strike
    """
    drilling_and_construction = models.ForeignKey(
        DrillingAndConstruction, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of feature'
    )
    description = models.TextField(
        null=True,
        blank=True)


class _CasingAndScreen(models.Model):
    """ Abstract model for Casing and Screen """
    drilling_and_construction = models.ForeignKey(
        DrillingAndConstruction, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    material = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="material of the feature."
    )

    class Meta:
        abstract = True


class Casing(_CasingAndScreen):
    """
    8.1.3 Casing
    Collection of linings of the borehole.
    """

    top_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the feature',
        related_name='casing_top_depth'
    )
    bottom_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the feature',
        related_name='casing_bottom_depth'
    )
    diameter = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Diameter of the feature',
        related_name='casing_diameter'
    )


class Screening(_CasingAndScreen):
    """
    8.1.12 Screen
    Collection of components of the water pump screen.
    """

    top_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the feature',
        related_name='screening_top_depth'
    )
    bottom_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the feature',
        related_name='screening_bottom_depth'
    )
    diameter = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Diameter of the feature',
        related_name='screening_diameter'
    )
