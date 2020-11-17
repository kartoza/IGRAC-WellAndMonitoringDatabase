import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from gwml2.models.well import (
    Well, WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)


# -------------------- WELL --------------------
@receiver(post_delete, sender=Well)
def post_delete_well(sender, instance, **kwargs):
    """ when deleted
    :type instance: Well
    """
    if instance.drilling:
        instance.drilling.delete()
    if instance.geology:
        instance.geology.delete()
    if instance.construction:
        instance.construction.delete()
    if instance.management:
        instance.management.delete()
    if instance.hydrogeology_parameter:
        instance.hydrogeology_parameter.delete()
    if instance.ground_surface_elevation:
        instance.ground_surface_elevation.delete()
    if instance.top_borehole_elevation:
        instance.top_borehole_elevation.delete()
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)


@receiver(post_save, sender=Well)
def update_well(sender, instance, **kwargs):
    """ when changed
    :type instance: Well
    """
    instance.updated()


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


# -------------------- MEASUREMENT --------------------
@receiver(post_delete, sender=WellLevelMeasurement)
@receiver(post_delete, sender=WellQualityMeasurement)
@receiver(post_delete, sender=WellYieldMeasurement)
def post_delete_measurement(sender, instance, **kwargs):
    if instance.value:
        instance.value.delete()


@receiver(post_save, sender=WellLevelMeasurement)
@receiver(post_save, sender=WellQualityMeasurement)
@receiver(post_save, sender=WellYieldMeasurement)
def post_save_measurement(sender, instance, **kwargs):
    """ when changed
    :type instance: WellLevelMeasurement
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass
