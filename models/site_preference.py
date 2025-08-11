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

    # Quality control
    groundwater_level_quality_control_days_gap = models.IntegerField(
        default=1095,
        help_text=(
            'Quality control days gap for groundwater level measurement. '
            'The gap is more than the value, it is basically a bad quality.'
        )
    )
    groundwater_level_quality_control_level_gap = models.IntegerField(
        default=50,
        help_text=(
            'Quality control level gap for groundwater level measurement. '
            'The gap is more than the value, it is basically a bad quality.'
        )
    )
    groundwater_level_strange_value_filter = models.TextField(
        default="value_in_m IN (0, -9999)",
        help_text=(
            'This is for query filter for the strange value.'
            'Use postgres filter syntax. '
        )
    )

    @staticmethod
    def update_running_harvesters():
        """Update running harvesters."""
        preferences = SitePreference.load()
        preferences.running_harvesters.set(
            Harvester.return_running_harvesters()
        )
