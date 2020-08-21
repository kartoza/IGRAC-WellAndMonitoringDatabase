from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermMeasurementParameter


class Measurement(models.Model):
    """ Model to hold measurement data
    """

    time = models.DateTimeField(
        null=True, blank=True,
        help_text='Reflects the time that the result applies to the measurement'
    )
    parameter = models.ForeignKey(
        TermMeasurementParameter, null=True, blank=True, verbose_name='parameter',
        help_text='This shall describe an arbitrary event-specific parameter. '
                  'This might be an environmental parameter, an instrument setting or input, '
                  'or an event-specific sampling parameter that is not tightly bound to either the feature-of-interest '
                  'or to the observation procedure (6.2.2.10).',
        on_delete=models.SET_NULL
    )
    methodology = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="Methodology of measurement."
    )
    quality = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='The quality of the result'
    )

    class Meta:
        abstract = True
