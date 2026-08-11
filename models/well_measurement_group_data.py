from django.contrib.gis.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASEUREMENT_LEVEL,
    MEASEUREMENT_QUALITY,
    MEASEUREMENT_YIELD,
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement,
)


class WellMeasurementGroupData(models.Model):
    """Well measurement group data by well x measurement x unit."""

    well = models.ForeignKey(Well, on_delete=models.CASCADE)
    unique_key = models.CharField()
    measurement_type = models.CharField()
    parameter = models.ForeignKey(
        TermMeasurementParameter, verbose_name=_("Parameter"), on_delete=models.CASCADE
    )
    unit = models.ForeignKey(
        Unit,
        help_text=_("Default Unit of measurement"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    begin_measurement = models.DateTimeField(null=True, blank=True)
    end_measurement = models.DateTimeField(null=True, blank=True)
    number_of_measurements = models.PositiveIntegerField()

    class Meta:
        unique_together = ("well", "measurement_type", "parameter", "unit")

    @staticmethod
    def create(well):
        """Create/update group data for a well from its measurements."""
        measurement_models = {
            MEASEUREMENT_LEVEL: WellLevelMeasurement,
            MEASEUREMENT_QUALITY: WellQualityMeasurement,
            MEASEUREMENT_YIELD: WellYieldMeasurement,
        }
        for measurement_type, MeasurementModel in measurement_models.items():
            rows = (
                MeasurementModel.objects.filter(well=well, default_value__isnull=False)
                .values("parameter_id", "default_unit_id")
                .annotate(
                    begin_measurement=models.Min("time"),
                    end_measurement=models.Max("time"),
                    number_of_measurements=Count("id"),
                )
            )
            for row in rows:
                WellMeasurementGroupData.objects.update_or_create(
                    well=well,
                    measurement_type=measurement_type,
                    parameter_id=row["parameter_id"],
                    unit_id=row["default_unit_id"],
                    defaults={
                        "begin_measurement": row["begin_measurement"],
                        "end_measurement": row["end_measurement"],
                        "number_of_measurements": row["number_of_measurements"],
                    },
                )
