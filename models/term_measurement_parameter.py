from adminsortable.models import Sortable
from django.contrib.gis.db import models

from gwml2.models.general import Unit
from gwml2.models.term import _Term


class TermMeasurementParameter(_Term):
    """ List of parameter for measurement."""

    units = models.ManyToManyField(
        Unit, null=True, blank=True
    )
    default_unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.CASCADE,
        related_name='term_measurement_parameter_default_unit'
    )

    def __str__(self):
        if self.description:
            return '{} ({})'.format(self.name, self.description)
        return self.name

    class Meta(Sortable.Meta):
        db_table = 'term_measurement_parameter'


class TermMeasurementParameterGroup(_Term):
    """ List of parameter for measurement."""
    parameters = models.ManyToManyField(
        TermMeasurementParameter,
        null=True, blank=True
    )

    class Meta(Sortable.Meta):
        db_table = 'term_measurement_parameter_group'
