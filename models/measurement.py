from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Quantity, Unit
from gwml2.models.metadata.creation import CreationMetadata
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.utilities import convert_value


class Measurement(CreationMetadata):
    """ Model to hold measurement data
    """

    time = models.DateTimeField(
        _('Time'),
        null=True, blank=True
    )
    parameter = models.ForeignKey(
        TermMeasurementParameter, null=True, blank=True,
        verbose_name=_('Parameter'),
        on_delete=models.SET_NULL
    )
    methodology = models.CharField(
        _('Methodology'),
        null=True, blank=True, max_length=200,
        help_text=_(
            "Explain the methodology used to collect the data, in the field and eventually in the lab.")
    )
    value = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Value')
    )

    # Default unit, to atomic all value in same units
    default_unit = models.ForeignKey(
        Unit,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    default_value = models.FloatField(
        null=True, blank=True
    )

    class Meta:
        abstract = True

    def set_default_value(self, init=False):
        """Set default."""
        if init and self.default_unit:
            return 'skip'
        if self.value:
            if not self.parameter.default_unit:
                self.default_unit = None
                self.default_value = self.value.value
            else:
                if self.parameter.default_unit != self.default_unit:
                    value = convert_value(
                        self.value, self.parameter.default_unit
                    )
                    if value and value.unit != self.default_unit:
                        self.default_unit = value.unit
                        self.default_value = value.value
                elif not self.default_unit:
                    self.default_unit = self.parameter.default_unit
                    self.default_value = self.value
        return None

    # ---------------------------------
    # Quality check
    # ---------------------------------
    @classmethod
    def longest_days_gap(cls, well_id, parameter_id=None):
        """Return quality check for time gap in days."""
        from django.db import connections
        query = f"""
            SELECT
                parameter_id,
                time AS current_time,
                prev_time,
                EXTRACT(EPOCH FROM (time - prev_time)) / 86400 AS gap_in_days
            FROM (
                SELECT
                    well_id,
                    parameter_id,
                    time,
                    LAG(time) OVER (
                        PARTITION BY well_id, parameter_id
                        ORDER BY time
                    ) AS prev_time
                FROM {cls._meta.db_table}
                WHERE well_id = {well_id}
                  {f"AND parameter_id = {parameter_id}" if parameter_id else ''}
                  AND time IS NOT NULL
            ) sub
            WHERE prev_time IS NOT NULL
            ORDER BY gap_in_days DESC
            LIMIT 1;
        """
        with connections['gwml2'].cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            try:
                value = rows[0]
                return {
                    "parameter_id": value[0],
                    "time": value[1].strftime('%Y-%m-%d %H:%M:%S'),
                    "previous_time": value[2].strftime('%Y-%m-%d %H:%M:%S'),
                    "gap_in_days": float(value[3])
                }
            except (KeyError, IndexError):
                return None
