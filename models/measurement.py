from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermMeasurementParameter


class Measurement(models.Model):
    """ Model to hold measurement data
    """

    time = models.DateTimeField(
        null=True, blank=True
    )
    parameter = models.ForeignKey(
        TermMeasurementParameter, null=True, blank=True, verbose_name='parameter',
        on_delete=models.SET_NULL
    )
    methodology = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="Explain the methodology used to collect the data, in the field and eventually in the lab."
    )
    value = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        abstract = True
