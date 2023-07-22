from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

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
