import datetime
import traceback
import typing
from abc import ABC, abstractmethod

import requests
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models.signals import post_save
from django.utils import timezone

from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterLog, RUNNING,
    ERROR, DONE, HarvesterWellData
)
from gwml2.models.general import Quantity, Unit
from gwml2.models.term import TermFeatureType
from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement
)
from gwml2.signals.well import post_save_measurement_for_cache
from gwml2.tasks.data_file_cache import generate_data_well_cache
from gwml2.tasks.well import generate_measurement_cache
from gwml2.utilities import temp_disconnect_signal, make_aware_local

User = get_user_model()


class HarvestingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BaseHarvester(ABC):
    """ Abstract class for harvester """
    attributes = {}

    def __init__(self, harvester: Harvester, replace: bool = False,
                 original_id: str = None):
        self.unit_m = Unit.objects.get(name='m')
        self.replace = replace
        self.original_id = original_id
        self.harvester = harvester
        for attribute in harvester.harvesterattribute_set.all():
            self.attributes[attribute.name] = attribute.value

        # check if it is already run
        if self.harvester.is_run:
            return
        if self.harvester.harvesterlog_set.filter(
                status=RUNNING
        ).first():
            return

        self.harvester.is_run = True
        self.harvester.save()
        self.log = HarvesterLog.objects.create(harvester=harvester)

        # run the process
        try:
            with temp_disconnect_signal(
                    signal=post_save,
                    receiver=post_save_measurement_for_cache,
                    sender=WellLevelMeasurement
            ):
                with temp_disconnect_signal(
                        signal=post_save,
                        receiver=post_save_measurement_for_cache,
                        sender=WellYieldMeasurement
                ):
                    with temp_disconnect_signal(
                            signal=post_save,
                            receiver=post_save_measurement_for_cache,
                            sender=WellQualityMeasurement
                    ):
                        self._process()
        except Exception:
            self._error(traceback.format_exc())

    @staticmethod
    def additional_attributes() -> dict:
        """
        Attributes that needs to be saved on database
        The value is the default value for the attribute
        """
        return {}

    @abstractmethod
    def _process(self):
        """ Run the harvester process"""

    @property
    def _headers(self) -> dict:
        return {}

    def _request_api(self, url: str):
        """ Request function"""
        try:
            response = requests.get(url, headers=self._headers)
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            return response.json()
        except (
                requests.exceptions.RequestException,
                requests.exceptions.HTTPError) as e:
            raise Exception('{} : {}'.format(url, e))

    def _error(self, message):
        self.harvester.is_run = False
        self.harvester.save()
        self.log.end_time = timezone.now()
        self.log.status = ERROR
        self.log.note = '{}'.format(message)
        self.log.save()
        print(self.log.note)

    def _done(self, message=''):
        self.harvester.is_run = False
        self.harvester.save()
        self.log.end_time = timezone.now()
        self.log.status = DONE
        self.log.note = message
        self.log.save()

    def _update(self, message=''):
        """ Update note for the log """
        self.log.note = message
        self.log.save()
        print(message)

    def get_well(self, original_id, latitude, longitude):
        """Return well."""
        wells = Well.objects.filter(
            original_id=original_id
        )
        if wells.count() > 0:
            wells = wells.filter(
                location__distance_lte=(
                    Point(longitude, latitude), D(m=200)
                )
            )
        # if the wells is 2 or more found, we skip it
        if wells.count() >= 2:
            raise Well.DoesNotExist()

        return wells.first()

    def _save_well(
            self,
            original_id: str,
            name: str,
            latitude: float,
            longitude: float,
            feature_type: typing.Optional[TermFeatureType] = None,
            ground_surface_elevation_masl: typing.Optional[float] = None,
            top_of_well_elevation_masl: typing.Optional[float] = None,
            description: typing.Optional[str] = None
    ):
        """ Save well """
        well = self.get_well(
            original_id, latitude=latitude, longitude=longitude
        )
        if self.harvester.save_missing_well:
            if not well:
                user_id = None
                try:
                    user_id = User.objects.get(username='admin').id
                except User.DoesNotExist:
                    pass
                well, created = Well.objects.get_or_create(
                    original_id=original_id,
                    location=Point(longitude, latitude),
                    defaults={
                        'name': name,
                        'organisation': self.harvester.organisation,
                        'feature_type': feature_type if feature_type else self.harvester.feature_type,
                        'created_by': user_id,
                        'last_edited_by': user_id,
                        'description': description
                    }
                )
                print(f'Well created : {well.id} - {well.original_id}')
            else:
                print(f'Found well : {well.id} - {well.original_id}')
        else:
            if not well:
                raise Well.DoesNotExist()

            print(f'Found well : {well.id} - {well.original_id}')
            if self.replace:
                WellLevelMeasurement.objects.filter(
                    well=well,
                ).delete()
                well.number_of_measurements = 0
                well.save()

            # TODO:
            #  We give option for harvester to force change the organisation
            # if well.organisation != self.harvester.organisation:
            #     well.organisation = self.harvester.organisation
            #     well.save()

        if not well.ground_surface_elevation and ground_surface_elevation_masl:
            well.ground_surface_elevation = Quantity.objects.create(
                value=ground_surface_elevation_masl,
                unit=self.unit_m
            )
            if not well.top_borehole_elevation and top_of_well_elevation_masl:
                well.top_borehole_elevation = Quantity.objects.create(
                    value=top_of_well_elevation_masl,
                    unit=self.unit_m
                )
            well.save()

        # create harvester well
        harvester_well_data, created = HarvesterWellData.objects.get_or_create(
            harvester=self.harvester,
            well=well
        )
        return well, harvester_well_data

    def _save_measurement(
            self,
            model: typing.Union[
                WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement],
            time: datetime,
            defaults: dict,
            harvester_well_data: HarvesterWellData,
            value: float = None,
            unit: Unit = None
    ):
        """ Save measurement """
        try:
            obj, created = model.objects.get_or_create(
                well=harvester_well_data.well,
                time=make_aware_local(time),
                parameter=defaults.get('parameter', None),
                defaults=defaults
            )
            if created:
                harvester_well_data.measurements_found += 1
                harvester_well_data.save()
        except (
                WellLevelMeasurement.MultipleObjectsReturned,
                WellQualityMeasurement.MultipleObjectsReturned,
                WellYieldMeasurement.MultipleObjectsReturned,
        ):
            obj = model.objects.filter(
                well=harvester_well_data.well,
                time=time,
                parameter=defaults.get('parameter', None)
            ).last()

        # Save value if not none
        if value is not None:
            if not obj.value:
                obj.value = Quantity.objects.create(
                    unit=unit,
                    value=value
                )
                obj.save()
        return obj

    def post_processing_well(
            self, well: Well, generate_country_cache: bool = True
    ):
        """Specifically for processing cache after procesing well."""
        print(f'Generate cache for {well.original_id}')
        well.update_metadata()
        generate_measurement_cache(well.id)
        generate_data_well_cache(
            well.id, generate_country_cache=generate_country_cache
        )
