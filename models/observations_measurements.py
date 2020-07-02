from django.contrib.gis.db import models
from gwml2.models.time import TMPeriod
from gwml2.models.universal import NamedValue


class OMProcess(models.Model):
    """
    OM_Process describes observation methods or the
    calculation of aquifer parameters
    """
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class OMObservation(models.Model):
    """
    Observation and Measurement model.
    """

    phenomenon_time = models.DateTimeField(
        null=True, blank=True, verbose_name='phenomenonTime',
        help_text='Reflects the time that the result applies to the property'
    )
    result_time = models.DateTimeField(
        null=True, blank=True, verbose_name='resultTime',
        help_text='The time at which the value has been obtained or became available'
    )
    valid_time = models.ForeignKey(
        TMPeriod, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='The time during which the value is usable.',
        verbose_name='validTime')
    resultQuality = models.TextField(
        null=True, blank=True, verbose_name='resultQuality',
        help_text='The quality of the result'
    )
    parameter = models.ManyToManyField(
        NamedValue, null=True, blank=True, verbose_name='parameter',
        help_text='This shall describe an arbitrary event-specific parameter. '
                  'This might be an environmental parameter, an instrument setting or input, '
                  'or an event-specific sampling parameter that is not tightly bound to either the feature-of-interest'
                  ' or to the observation procedure (6.2.2.10).'
    )
