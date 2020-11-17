from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gwml2.models.well import Well
from gwml2.models.drilling import Drilling, StratigraphicLog, WaterStrike


@receiver(post_save, sender=Drilling)
def drilling_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: Drilling
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(post_delete, sender=StratigraphicLog)
def delete_stratigraphic_log(sender, instance, **kwargs):
    """ when deleted
    :type instance: StratigraphicLog
    """
    if instance.top_depth:
        instance.top_depth.delete()
    if instance.bottom_depth:
        instance.bottom_depth.delete()


@receiver(post_delete, sender=WaterStrike)
def delete_water_strike(sender, instance, **kwargs):
    """ when deleted
    :type instance: WaterStrike
    """
    if instance.depth:
        instance.depth.delete()


@receiver(post_save, sender=StratigraphicLog)
@receiver(post_delete, sender=StratigraphicLog)
@receiver(post_save, sender=WaterStrike)
@receiver(post_delete, sender=WaterStrike)
def drilling_related_object_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: StratigraphicLog
    """
    try:
        if instance.drilling.well:
            instance.drilling.well.updated()
    except (Drilling.DoesNotExist, Well.DoesNotExist):
        pass
