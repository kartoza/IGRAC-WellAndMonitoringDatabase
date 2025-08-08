import json

from django.db.models.signals import post_save
from django.utils import timezone

from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter, TermMeasurementParameterGroup
)
from gwml2.models.well import (
    Well, WellLevelMeasurement
)
from gwml2.signals.well import update_well
from gwml2.utilities import temp_disconnect_signal


class WellQualityControl:
    """Doing quality control on well."""

    def __init__(self, well: Well):
        self.well = well

    def gap_time_quality(self):
        """Check if gap time is less than 3 years."""
        from gwml2.models.site_preference import SitePreference
        preferences = SitePreference.load()
        gap_limit = preferences.quality_control_days_gap

        quality = []

        def save_value(_value):
            try:
                if _value['gap_in_days'] >= gap_limit:
                    quality.append(_value)
            except KeyError:
                pass

        # Check for well level measurement
        value = WellLevelMeasurement.longest_days_gap(self.well.id)
        save_value(value)

        # Check other parameters
        for parameter in TermMeasurementParameter.objects.all():
            try:
                model = TermMeasurementParameterGroup.get_measurement_model(
                    parameter
                )
                if model != WellLevelMeasurement:
                    value = model.longest_days_gap(
                        self.well.id, parameter_id=parameter.id
                    )
                    save_value(value)
            except KeyError:
                pass

        # Save the well
        with temp_disconnect_signal(
                signal=post_save,
                receiver=update_well,
                sender=Well
        ):
            if quality:
                self.well.bad_quality_time_gap = json.dumps(quality)
            else:
                self.well.bad_quality_time_gap = None
            self.well.bad_quality_time_gap_generated_time = timezone.now()
            self.well.save()
