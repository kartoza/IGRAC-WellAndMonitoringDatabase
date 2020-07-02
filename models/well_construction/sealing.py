from django.contrib.gis.db import models
from gwml2.models.observations_measurements import OMProcess
from gwml2.models.well_construction.casing_component import CasingComponent
from gwml2.models.well_construction.sealing_component import SealingComponent


class Sealing(models.Model):
    """
    8.1.14 Sealing
    Collection of materials that prevent
    undesirable elements from entering the borehole.
    """
    sealing_grouting_placement_method = models.ForeignKey(
        OMProcess,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='sealingGroutingPlacementMethod',
        help_text="Method of placing the sealing grouting.")

    casing_left = models.ManyToManyField(
        CasingComponent,
        related_name='casing_left',
        null=True, blank=True,
        verbose_name='casingLeft',
        help_text="Casing left after plugging.")

    casing_slit = models.ManyToManyField(
        CasingComponent,
        related_name='casing_slit',
        null=True, blank=True,
        verbose_name='casingSlit',
        help_text="Casing slit opposing water bearing zones before plugging.")

    sealing_element = models.ManyToManyField(
        SealingComponent,
        null=True, blank=True,
        verbose_name='sealingElement',
        help_text="Relation between a seal and its parts.")
