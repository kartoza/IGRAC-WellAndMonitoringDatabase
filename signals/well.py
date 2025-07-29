import os

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from gwml2.models.well import (
    Well, WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.tasks.well import generate_measurement_cache
from gwml2.utilities import make_aware_local


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
    if instance.glo_90m_elevation:
        instance.glo_90m_elevation.delete()
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)

    instance.remove_cache()


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


@receiver(post_delete, sender=WellLevelMeasurement)
@receiver(post_delete, sender=WellQualityMeasurement)
@receiver(post_delete, sender=WellYieldMeasurement)
def post_delete_measurement_trigger_well_update(sender, instance, **kwargs):
    try:
        if sender == WellLevelMeasurement:
            instance.well.number_of_measurements_level -= 1
        elif sender == WellQualityMeasurement:
            instance.well.number_of_measurements_quality -= 1
        elif sender == WellYieldMeasurement:
            instance.well.number_of_measurements_yield -= 1
        instance.well.number_of_measurements -= 1
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(pre_save, sender=WellLevelMeasurement)
@receiver(pre_save, sender=WellQualityMeasurement)
@receiver(pre_save, sender=WellYieldMeasurement)
def pre_save_measurement(sender, instance, **kwargs):
    """ when changed
    :type instance: WellLevelMeasurement
    """
    try:
        if not instance.id:
            instance.well.number_of_measurements += 1
            if sender == WellLevelMeasurement:
                instance.well.number_of_measurements_level += 1
            elif sender == WellQualityMeasurement:
                instance.well.number_of_measurements_quality += 1
            elif sender == WellYieldMeasurement:
                instance.well.number_of_measurements_yield += 1

        instance.set_default_value()

        # Check instance of time
        instance_time = make_aware_local(instance.time)
        first_time = make_aware_local(
            instance.well.first_time_measurement
        )
        if not first_time or instance_time < first_time:
            instance.well.first_time_measurement = instance_time

        last_time = make_aware_local(
            instance.well.last_time_measurement
        )
        if not last_time or instance_time > last_time:
            instance.well.last_time_measurement = instance_time
    except Well.DoesNotExist:
        pass


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


@receiver(post_save, sender=WellLevelMeasurement)
@receiver(post_save, sender=WellQualityMeasurement)
@receiver(post_save, sender=WellYieldMeasurement)
def post_save_measurement_for_cache(sender, instance, **kwargs):
    """ when changed
    :type instance: WellLevelMeasurement
    """
    generate_measurement_cache.delay(
        instance.well.id, sender.__name__
    )
