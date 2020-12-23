from datetime import datetime
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils.timezone import make_aware

from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.drilling import Drilling
from gwml2.models.construction import Construction
from gwml2.models.metadata.creation import CreationMetadata
from gwml2.models.metadata.license_metadata import LicenseMetadata
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.term import TermWellPurpose, TermWellStatus
from gwml2.models.well_management.organisation import Organisation
from gwml2.utilities import temp_disconnect_signal


class Well(GeneralInformation, CreationMetadata, LicenseMetadata):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""
    ggis_uid = models.CharField(
        max_length=256,
        null=True, blank=True,
        help_text='organisation name + Original ID'
    )

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

    # metadata
    affiliate_organisations = models.ManyToManyField(
        Organisation, null=True, blank=True,
        related_name='well_affiliate_organisations'
    )
    public = models.BooleanField(
        default=True,
        help_text='indicate that well can be viewed by '
                  'non organisation user'
    )

    def __str__(self):
        return self.original_id

    class Meta:
        db_table = 'well'
        ordering = ['original_id']

    def updated(self):
        """ update time updated when well updated """
        from gwml2.signals.well import update_well
        with temp_disconnect_signal(
                signal=post_save,
                receiver=update_well,
                sender=Well
        ):
            self.last_edited_at = make_aware(datetime.now())
            if self.organisation:
                self.ggis_uid = '{}-{}'.format(self.organisation.name, self.original_id)
            try:
                self.save()
            except (ValueError, KeyError):
                pass

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
        if self.public:
            return True
        if not self.organisation:
            return True
        if not user:
            return False
        if user.is_staff:
            return True

        accessible = user.id in self.organisation.viewers or user.id in self.organisation.editors or user.id in self.organisation.admins
        if not accessible:
            """ Check from affiliate organisation """
            for org in self.affiliate_organisations.all():
                if user.id in org.viewers or user.id in org.editors or user.id in org.admins:
                    return True
        return accessible

    def editor_permission(self, user):
        """ Return editor permission from user id

        :param user: user to be checked
        :type user: User

        :return: permission
        :rtype: bool
        """
        if not user:
            return False
        elif user.is_staff:
            return True

        if not self.organisation:
            return False
        return user.id in self.organisation.editors or user.id in self.organisation.admins


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


class WellQualityMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_quality_measurement'
        ordering = ('-time',)


class WellYieldMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_yield_measurement'
        ordering = ('-time',)
