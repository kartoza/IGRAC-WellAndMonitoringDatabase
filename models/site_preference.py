from django.db import models

from core.singleton import SingletonModel
from gwml2.models.term_measurement_parameter import TermMeasurementParameter


class SitePreference(SingletonModel):
    """Model to define site preferences."""
    parameter_from_ground_surface = models.ForeignKey(
        TermMeasurementParameter,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='site_preference_parameter_from_ground_surface'
    )
    parameter_from_top_well = models.ForeignKey(
        TermMeasurementParameter,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='site_preference_parameter_from_top_well'
    )
    parameter_amsl = models.ForeignKey(
        TermMeasurementParameter,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='site_preference_parameter_amsl'
    )
