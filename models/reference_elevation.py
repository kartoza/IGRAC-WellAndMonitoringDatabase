from django.contrib.gis.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from gwml2.models.general import Quantity
from gwml2.models.term import TermReferenceElevationType


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
        TermReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    description = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return '{} ({})'.format(self.value.value, self.value.unit)

    class Meta:
        db_table = 'reference_elevation'


@receiver(post_delete, sender=ReferenceElevation)
def delete_referenceelevation(sender, instance, **kwargs):
    if instance.value:
        instance.value.delete()
