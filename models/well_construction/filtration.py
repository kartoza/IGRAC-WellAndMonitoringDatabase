from django.contrib.gis.db import models
from gwml2.models.well_construction.filtration_component import FiltrationComponent


class Filtration(models.Model):
    """
    8.1.7 Filtration
    Collection of filtration components used to filter a fluid body in a well.
    """

    name = models.TextField(null=True, blank=True)
    filter_element = models.ManyToManyField(
        FiltrationComponent, null=True, blank=True,
        verbose_name='filterElement',
        help_text="Relation between a filtration device and its parts.")

    def __str__(self):
        return self.name
