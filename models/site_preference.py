from django.db import models

from core.singleton import SingletonModel
from gwml2.harvesters.models import Harvester
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
    batch_upload_auto_resume = models.BooleanField(
        default=False,
        help_text='Auto resume flag for batch upload.'
    )

    # Harvester
    running_harvesters_concurrency_count = models.IntegerField(
        default=2
    )
    running_harvesters = models.ManyToManyField(
        Harvester, blank=True
    )

    @staticmethod
    def update_running_harvesters():
        """Update running harvesters."""
        preferences = SitePreference.load()
        preferences.running_harvesters.set(
            Harvester.return_running_harvesters()
        )
