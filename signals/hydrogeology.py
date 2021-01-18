from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gwml2.models.well import Well
from gwml2.models.hydrogeology import PumpingTest, HydrogeologyParameter


@receiver(post_save, sender=PumpingTest)
@receiver(post_delete, sender=PumpingTest)
def pumpingtest_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: PumpingTest
    """
    try:
        instance.hydrogeologyparameter.well.updated()
    except (HydrogeologyParameter.DoesNotExist, Well.DoesNotExist):
        pass


@receiver(post_delete, sender=PumpingTest)
def delete_pumpingtest(sender, instance, **kwargs):
    if instance.specific_capacity:
        instance.specific_capacity.delete()
    if instance.hydraulic_conductivity:
        instance.hydraulic_conductivity.delete()
    if instance.transmissivity:
        instance.transmissivity.delete()
    if instance.specific_storage:
        instance.specific_storage.delete()
    if instance.storativity:
        instance.storativity.delete()


@receiver(post_save, sender=HydrogeologyParameter)
def hydrogeologyparameter_changed(sender, instance, **kwargs):
    """ when changed
    :type instance: HydrogeologyParameter
    """
    try:
        instance.well.updated()
    except Well.DoesNotExist:
        pass


@receiver(post_delete, sender=HydrogeologyParameter)
def delete_hydrogeologyparameter(sender, instance, **kwargs):
    if instance.pumping_test:
        instance.pumping_test.delete()
