from django.contrib.gis.db import models
from adminsortable.models import Sortable

from gwml2.models.general import Quantity
from gwml2.models.term import _Term


class ReferenceElevationType(_Term):
    """
    The type of reference for elevation
    """

    class Meta(Sortable.Meta):
        db_table = 'reference_elevation_type'


class ReferenceElevation(models.Model):
    """
    7.6.2 Elevation
    Elevation of a feature in reference to a reference type.

    """
    value = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    reference = models.ForeignKey(
        ReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    description = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return '{} ({})'.format(self.value.value, self.value.unit)

    class Meta:
        db_table = 'reference_elevation'
