from django.contrib.gis.db import models
from gwml2.models.well_construction.casing_component import CasingComponent


class Casing(models.Model):
    """
    8.1.3 Casing
    Collection of linings of the borehole.
    """

    name = models.TextField(null=True, blank=True)
    casing_element = models.ManyToManyField(
        CasingComponent, null=True, blank=True,
        verbose_name='casingElement',
        help_text="Relation between a casing and its parts.")

    def __str__(self):
        return self.name
