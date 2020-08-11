from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.reference_elevation import ReferenceElevation


class Construction(models.Model):
    """ Construction
    """
    reference_elevation = models.OneToOneField(
        ReferenceElevation, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    pump_installer = models.CharField(
        null=True, blank=True, max_length=512)
    pump_description = models.TextField(
        null=True,
        blank=True)


class _CasingAndScreen(models.Model):
    """ Abstract model for Casing and Screen """
    construction = models.ForeignKey(
        Construction, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    material = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="material of the feature."
    )
    description = models.TextField(
        null=True,
        blank=True)

    class Meta:
        abstract = True


class Casing(_CasingAndScreen):
    """
    8.1.3 Casing
    Collection of linings of the borehole.
    """

    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the feature',
        related_name='casing_top_depth'
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the feature',
        related_name='casing_bottom_depth'
    )
    diameter = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Diameter of the feature',
        related_name='casing_diameter'
    )


class Screen(_CasingAndScreen):
    """
    8.1.12 Screen
    Collection of components of the water pump screen.
    """

    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the feature',
        related_name='screening_top_depth'
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the feature',
        related_name='screening_bottom_depth'
    )
    diameter = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Diameter of the feature',
        related_name='screening_diameter'
    )
