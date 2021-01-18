from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gwml2.models.well import Well
from gwml2.models.geology import Geology


@receiver(post_save, sender=Geology)
def geology_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: Geology
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(post_delete, sender=Geology)
def delete_geology(sender, instance, **kwargs):
    if instance.total_depth:
        instance.total_depth.delete()
