import gzip
import json
import os
from datetime import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _

from gwml2.models.construction import Construction
from gwml2.models.document import Document
from gwml2.models.drilling import Drilling
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.management import Management
from gwml2.models.measurement import Measurement
from gwml2.models.metadata.creation import CreationMetadata
from gwml2.models.metadata.license_metadata import LicenseMetadata
from gwml2.models.term import TermWellPurpose, TermWellStatus
from gwml2.models.well_management.organisation import Organisation
from gwml2.utilities import temp_disconnect_signal, convert_value

MEASUREMENT_PARAMETER_AMSL = 'Water level elevation a.m.s.l.'
MEASUREMENT_PARAMETER_TOP = 'Water depth [from the top of the well]'
MEASUREMENT_PARAMETER_GROUND = 'Water depth [from the ground surface]'


class WellManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(organisation__active=True)


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
        null=True, blank=True,
        verbose_name=_('Purpose')
    )
    status = models.ForeignKey(
        TermWellStatus, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Status')
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
        null=True, blank=True,
        verbose_name=_('Organisation')
    )

    # First and last measurement time
    first_time_measurement = models.DateTimeField(
        _('Time'),
        null=True, blank=True
    )
    last_time_measurement = models.DateTimeField(
        _('Time'),
        null=True, blank=True
    )

    # number of measurement
    number_of_measurements = models.IntegerField(
        default=0,
        help_text=_('Indicate how many measurement this well has.')
    )
    number_of_measurements_level = models.IntegerField(
        default=0,
        help_text=_('Indicate how many level measurement this well has.')
    )
    number_of_measurements_quality = models.IntegerField(
        default=0,
        help_text=_('Indicate how many quality measurement this well has.')
    )
    number_of_measurements_yield = models.IntegerField(
        default=0,
        help_text=_('Indicate how many yield measurement this well has.')
    )
    objects = WellManager()

    def __str__(self):
        return self.original_id

    class Meta:
        db_table = 'well'
        ordering = ['original_id']

    def assign_country(self, force=False):
        """Assign country to the well."""
        from gwml2.models.general_information import Country
        if not self.country or force:
            country = Country.objects.filter(
                geometry__contains=self.location
            ).first()
            if country:
                self.country = country
                self.save()

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
                self.ggis_uid = '{}-{}'.format(
                    self.organisation.name, self.original_id
                )
            self.assign_country()
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
        return True

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

    def return_measurement_cache_path(self, measurement_name: str):
        """
        Return file path of cache file
        """
        folder = os.path.join(settings.MEDIA_ROOT, 'measurement-cache',
                              '{}'.format(self.id))
        return os.path.join(folder, '{}.gz'.format(measurement_name))

    def measurement_data(self, measurement_name: str):
        """ Return measurement data """
        ground_surface_elevation = self.ground_surface_elevation
        unit_to = None
        if ground_surface_elevation:
            unit_to = ground_surface_elevation.unit
        top_borehole_elevation = self.top_borehole_elevation
        if top_borehole_elevation:
            if not unit_to:
                unit_to = top_borehole_elevation.unit
            top_borehole_elevation = convert_value(
                top_borehole_elevation, unit_to)

        for MeasurementModel in \
                [WellLevelMeasurement, WellQualityMeasurement,
                 WellYieldMeasurement]:
            if MeasurementModel.__name__ == measurement_name:
                output = {"data": [], "page": 1, "end": True}
                for measurement in MeasurementModel.objects.filter(well=self):
                    quantity = convert_value(measurement.value, unit_to)
                    if not quantity:
                        continue

                    value = quantity.value
                    unit = ''
                    if quantity.unit:
                        unit = quantity.unit.name

                    parameter = measurement.parameter.name

                    if MeasurementModel == WellLevelMeasurement:
                        if parameter in [MEASUREMENT_PARAMETER_AMSL, MEASUREMENT_PARAMETER_TOP, MEASUREMENT_PARAMETER_GROUND]:
                            parameter = MEASUREMENT_PARAMETER_AMSL
                            if measurement.parameter.name == MEASUREMENT_PARAMETER_TOP:
                                if top_borehole_elevation:
                                    value = top_borehole_elevation.value - value
                                else:
                                    parameter = measurement.parameter.name
                            elif measurement.parameter.name == MEASUREMENT_PARAMETER_GROUND:
                                if ground_surface_elevation:
                                    value = ground_surface_elevation.value - value
                                else:
                                    parameter = measurement.parameter.name

                    try:
                        value = round(value, 3)
                    except ValueError:
                        pass

                    output['data'].append({
                        'dt': measurement.time.timestamp(),
                        'par': parameter,
                        'u': unit,
                        'v': value
                    })
                return output
        return None

    def generate_measurement_cache(self, model=None):
        """ Generate measurement cache """
        folder = os.path.join(
            settings.MEDIA_ROOT, 'measurement-cache', '{}'.format(self.id)
        )
        if not os.path.exists(folder):
            os.makedirs(folder)

        for MeasurementModel in \
                [WellLevelMeasurement, WellQualityMeasurement,
                 WellYieldMeasurement]:
            measurement_name = MeasurementModel.__name__
            if model and measurement_name != model:
                continue
            output = self.measurement_data(measurement_name)
            if output:
                json_str = json.dumps(output) + "\n"
                json_bytes = json_str.encode('utf-8')

                filename = self.return_measurement_cache_path(measurement_name)
                if os.path.exists(filename):
                    os.remove(filename)
                file = gzip.open(filename, 'wb')
                file.write(json_bytes)
                file.close()


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

    value_in_m = models.FloatField(
        editable=False,
        null=False,
        blank=False,
        default=0.0,
        help_text='Converted value in meters'
    )

    class Meta:
        db_table = 'well_level_measurement'
        ordering = ('-time',)


@receiver(post_save, sender=WellLevelMeasurement)
def update_value_in_m(sender, instance, **kwargs):
    if not instance.value or not instance.value.unit:
        return
    if instance.value.unit.name == 'ft':
        instance.value_in_m = instance.value.value * 0.3048
    else:
        instance.value_in_m = instance.value.value
    post_save.disconnect(update_value_in_m, sender=WellLevelMeasurement)
    instance.save()
    post_save.connect(update_value_in_m, sender=WellLevelMeasurement)


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
