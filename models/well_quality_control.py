import json

from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from gwml2.models.well import Well


class WellQualityControl(models.Model):
    """Quality control data for well."""
    well = models.OneToOneField(Well, on_delete=models.CASCADE)

    # ---------------------------
    # Quality control
    # ---------------------------
    groundwater_level_time_gap = models.JSONField(
        null=True, blank=True,
        help_text=_(
            'Filled with some of bad quality info by time gap '
            'for Groundwater level measurement.'
        )
    )
    groundwater_level_time_gap_generated_time = models.DateTimeField(
        null=True, blank=True
    )
    groundwater_level_value_gap = models.JSONField(
        null=True, blank=True,
        help_text=_(
            'Filled with some of bad quality info by level gap '
            'for Groundwater level measurement.'
        )
    )
    groundwater_level_value_gap_generated_time = models.DateTimeField(
        null=True, blank=True
    )
    groundwater_level_strange_value = models.JSONField(
        null=True, blank=True,
        help_text=_(
            'Filled with some of bad quality info by strange value '
            'for Groundwater level measurement.'
        )
    )
    groundwater_level_strange_value_generated_time = models.DateTimeField(
        null=True, blank=True
    )

    class Meta:
        db_table = 'well_quality_control'

    # ------------------------------------------------------
    # QUALITY CONTROL UITILITIES
    # ------------------------------------------------------
    def run(self):
        """Run quality control."""
        self.gap_time_quality()
        self.gap_level_quality()

    def gap_time_quality(self):
        """Check if gap time."""
        from gwml2.models.well import WellLevelMeasurement
        from gwml2.signals.well import update_well
        from gwml2.utilities import temp_disconnect_signal
        from gwml2.models.site_preference import SitePreference
        preferences = SitePreference.load()
        gap_limit = preferences.groundwater_level_quality_control_days_gap

        quality = []

        def save_value(_value):
            try:
                if _value['gap'] >= gap_limit:
                    quality.append(_value)
            except (TypeError, KeyError):
                pass

        # Check for well level measurement
        value = WellLevelMeasurement.longest_days_gap(self.well.id)
        save_value(value)

        # Save the well
        with temp_disconnect_signal(
                signal=post_save,
                receiver=update_well,
                sender=Well
        ):
            if quality:
                self.groundwater_level_time_gap = json.dumps(quality)
            else:
                self.groundwater_level_time_gap = None
            self.groundwater_level_time_gap_generated_time = timezone.now()
            self.save()

    def gap_level_quality(self):
        """Check if gap level."""
        from gwml2.models.site_preference import SitePreference

        from gwml2.models.well import WellLevelMeasurement
        from gwml2.signals.well import update_well
        from gwml2.utilities import temp_disconnect_signal
        preferences = SitePreference.load()
        gap_limit = preferences.groundwater_level_quality_control_level_gap

        quality = []

        def save_value(_value):
            try:
                if _value['gap'] >= gap_limit:
                    quality.append(_value)
            except (TypeError, KeyError):
                pass

        # Check for well level measurement
        value = WellLevelMeasurement.longest_level_gap(self.well.id)
        save_value(value)

        # Save the well
        with temp_disconnect_signal(
                signal=post_save,
                receiver=update_well,
                sender=Well
        ):
            if quality:
                self.groundwater_level_value_gap = json.dumps(quality)
            else:
                self.groundwater_level_value_gap = None
            self.groundwater_level_value_gap_generated_time = timezone.now()
            self.save()
