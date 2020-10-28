__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '27/08/20'

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.gis.db import models
from gwml2.models.general import Quantity


class Geology(models.Model):
    """ Geology
    """
    total_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Depth of the well below the ground surface.'
    )

    class Meta:
        db_table = 'geology'


@receiver(post_delete, sender=Geology)
def delete_geology(sender, instance, **kwargs):
    if instance.total_depth:
        instance.total_depth.delete()
