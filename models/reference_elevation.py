from django.contrib.gis.db import models
from gwml2.models.general import Quantity


class ReferenceElevation(models.Model):
    """
    7.6.2 Elevation
    Elevation of a feature in reference to a datum.

    """
    value = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    description = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return '{} ({})'.format(self.value.value, self.value.unit)

    class Meta:
        db_table = 'reference_elevation'
