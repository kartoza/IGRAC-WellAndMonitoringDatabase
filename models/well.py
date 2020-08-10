import os
from django.contrib.gis.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.drilling_and_construction import DrillingAndConstruction
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.term import TermWellPurpose


class Well(GeneralInformation):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""
    original_id = models.CharField(
        unique=True, max_length=256)
    purpose = models.ForeignKey(
        TermWellPurpose, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    geology = models.ForeignKey(
        Geology, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    drilling_and_construction = models.ForeignKey(
        DrillingAndConstruction, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    management = models.ForeignKey(
        Management, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    hydrogeology_parameter = models.ForeignKey(
        HydrogeologyParameter, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.original_id

    class Meta:
        ordering = ['original_id']


class WellMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )


class WellDocument(Document):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )


@receiver(post_delete, sender=Well)
def delete_well(sender, instance, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)


@receiver(pre_save, sender=Well)
def pre_save_well(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).photo
    except sender.DoesNotExist:
        return False

    new_file = instance.photo
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(post_save, sender=WellDocument)
def update_document(sender, instance, **kwargs):
    """
    When file is cleared, automatically delete the document
    """
    if not instance.file:
        instance.delete()
    else:
        if instance.file_path != instance.file.path:
            instance.file_path = instance.file.path
            instance.save()


@receiver(post_delete, sender=WellDocument)
def delete_document(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file_path):
            os.remove(instance.file_path)


@receiver(pre_save, sender=WellDocument)
def pre_save_document(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file
    except sender.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)
