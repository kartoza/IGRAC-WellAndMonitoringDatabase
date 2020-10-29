from django.contrib.gis.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from django.db.models.signals import post_delete
from django.dispatch import receiver
from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.drilling import Drilling
from gwml2.models.construction import Construction
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.term import TermWellPurpose, TermWellStatus
from gwml2.models.well_management.organisation import Organisation


class Well(GeneralInformation):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""
    purpose = models.ForeignKey(
        TermWellPurpose, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    status = models.ForeignKey(
        TermWellStatus, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    drilling = models.OneToOneField(
        Drilling, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    geology = models.OneToOneField(
        Geology, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    construction = models.OneToOneField(
        Construction, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    management = models.OneToOneField(
        Management, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    hydrogeology_parameter = models.OneToOneField(
        HydrogeologyParameter, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # this is for management
    organisation = models.ForeignKey(
        Organisation, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.original_id

    class Meta:
        db_table = 'well'
        ordering = ['original_id']

    def relation_queryset(self, relation_model_name):
        """ Return queryset of relation of model
        """
        if relation_model_name == 'WellDocument':
            return self.welldocument_set
        elif relation_model_name == 'WaterStrike':
            if self.drilling:
                return self.drilling.waterstrike_set
        elif relation_model_name == 'StratigraphicLog':
            if self.drilling:
                return self.drilling.stratigraphiclog_set
        elif relation_model_name == 'ConstructionStructure':
            if self.construction:
                return self.construction.constructionstructure_set
        elif relation_model_name == 'WellLevelMeasurement':
            return self.welllevelmeasurement_set
        elif relation_model_name == 'WellQualityMeasurement':
            return self.wellqualitymeasurement_set
        elif relation_model_name == 'WellYieldMeasurement':
            return self.wellyieldmeasurement_set
        return None

    def view_permission(self, user):
        """ Return view permission from user id

        :param user: user to be checked
        :type user: User

        :return: permission
        :rtype: bool
        """
        if not self.organisation:
            return True
        if not user:
            return False
        else:
            if user.is_staff:
                return True
            return user.id in self.organisation.viewers

    def editor_permission(self, user):
        """ Return editor permission from user id

        :param user: user to be checked
        :type user: User

        :return: permission
        :rtype: bool
        """
        if not self.organisation:
            return True
        if not user:
            return False
        else:
            if user.is_staff:
                return True
            return user.id in self.organisation.editors


@receiver(post_delete, sender=Well)
def delete_well(sender, instance, **kwargs):
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


# documents
class WellDocument(Document):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_document'


# Monitoring data
class WellLevelMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_level_measurement'
        ordering = ('-time',)


@receiver(post_delete, sender=WellLevelMeasurement)
def delete_welllevelmeasurement(sender, instance, **kwargs):
    if instance.value:
        instance.value.delete()


class WellQualityMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_quality_measurement'
        ordering = ('-time',)


@receiver(post_delete, sender=WellQualityMeasurement)
def delete_wellqualitymeasurement(sender, instance, **kwargs):
    if instance.value:
        instance.value.delete()


class WellYieldMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_yield_measurement'
        ordering = ('-time',)


@receiver(post_delete, sender=WellYieldMeasurement)
def delete_wellyieldmeasurement(sender, instance, **kwargs):
    if instance.value:
        instance.value.delete()
