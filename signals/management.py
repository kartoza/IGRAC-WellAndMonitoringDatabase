from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gwml2.models.well import Well
from gwml2.models.management import License, Management


@receiver(post_save, sender=License)
@receiver(post_delete, sender=License)
def license_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: License
    """
    try:
        instance.management.well.updated()
    except (Management.DoesNotExist, Well.DoesNotExist):
        pass


@receiver(post_save, sender=Management)
def management_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: Management
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(post_delete, sender=Management)
def delete_management(sender, instance, **kwargs):
    if instance.license:
        instance.license.delete()
