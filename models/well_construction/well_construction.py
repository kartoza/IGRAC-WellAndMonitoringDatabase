from django.contrib.gis.db import models
from gwml2.models.well_construction.casing import Casing
from gwml2.models.well_construction.filtration import Filtration
from gwml2.models.well_construction.screen import Screen
from gwml2.models.well_construction.sealing import Sealing


class WellConstruction(models.Model):
    """
    8.1.16 WellConstruction
    Construction components of the well. These are particularly important when assessing
    results of pump tests.
    """

    name = models.TextField(null=True, blank=True)
    casing = models.ForeignKey(
        Casing, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Casing',
        help_text="A casing is a type of well construction entity.")
    screen = models.ForeignKey(
        Screen, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Screen',
        help_text="A screen is a type of well construction entity.")
    filtration = models.ForeignKey(
        Filtration, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Filtration',
        help_text="A sealing is a type of well construction entity.")
    sealing = models.ForeignKey(
        Sealing, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Sealing',
        help_text="A sealing is a type of well construction entity.")

    def __str__(self):
        return self.name
