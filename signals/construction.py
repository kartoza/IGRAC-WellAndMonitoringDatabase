from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gwml2.models.well import Well
from gwml2.models.construction import Construction, ConstructionStructure


@receiver(post_save, sender=Construction)
def construction_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: Construction
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(post_delete, sender=ConstructionStructure)
def delete_structure(sender, instance, **kwargs):
    if instance.top_depth:
        instance.top_depth.delete()
    if instance.bottom_depth:
        instance.bottom_depth.delete()
    if instance.diameter:
        instance.diameter.delete()


@receiver(post_save, sender=ConstructionStructure)
@receiver(post_delete, sender=ConstructionStructure)
def construction_structure_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: ConstructionStructure
    """
    try:
        if instance.construction.well:
            instance.construction.well.updated()
    except (Construction.DoesNotExist, Well.DoesNotExist):
        pass
