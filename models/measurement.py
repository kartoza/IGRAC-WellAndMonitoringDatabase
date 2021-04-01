from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from gwml2.models.general import Quantity
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.metadata.creation import CreationMetadata


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
        help_text=_("Explain the methodology used to collect the data, in the field and eventually in the lab.")
    )
    value = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Value')
    )

    class Meta:
        abstract = True
