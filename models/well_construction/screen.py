from django.contrib.gis.db import models
from gwml2.models.well_construction.screen_component import ScreenComponent


class Screen(models.Model):
    """
    8.1.12 Screen
    Collection of components of the water pump screen.
    """

    name = models.TextField(null=True, blank=True)
    screen_element = models.ManyToManyField(
        ScreenComponent, null=True, blank=True,
        verbose_name='screenElement',
        help_text="Relation between a screen and its parts.")

    def __str__(self):
        return self.name
