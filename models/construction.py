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
        null=True, blank=True, max_length=512,
        help_text="Name of the company or person who installed the pump."
    )
    pump_description = models.TextField(
        null=True,
        blank=True,
        help_text="Any relevant information on the pump (e.g. model, capacity, energy supply, depth)."
    )

    class Meta:
        db_table = 'construction'


class _CasingAndScreen(models.Model):
    """ Abstract model for Casing and Screen """
    construction = models.ForeignKey(
        Construction, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    material = models.CharField(
        null=True, blank=True, max_length=512
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
        related_name='casing_top_depth'
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='casing_bottom_depth'
    )
    diameter = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='casing_diameter'
    )

    class Meta:
        db_table = 'construction_casing'


class Screen(_CasingAndScreen):
    """
    8.1.12 Screen
    Collection of components of the water pump screen.
    """

    top_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='screening_top_depth'
    )
    bottom_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='screening_bottom_depth'
    )
    diameter = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='screening_diameter'
    )

    class Meta:
        db_table = 'construction_screen'
