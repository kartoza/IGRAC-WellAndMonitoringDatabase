import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from gwml2.models.well import Well, WellDocument


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
