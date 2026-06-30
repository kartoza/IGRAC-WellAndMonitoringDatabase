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
    HarvesterLog, RUNNING, ERROR,
    DONE, Harvester, HarvesterAttribute,
    HarvesterParameterMap
)
from gwml2.models.general import Quantity, Unit
from gwml2.models.term import TermFeatureType
from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement
)
from gwml2.models.well_materialized_view import MaterializedViewWell
from gwml2.signals.well import post_save_measurement
from gwml2.tasks.well_file_cache import generate_data_well_cache
from gwml2.tasks.well_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.well_file_cache.organisation_cache import (
    generate_data_organisation_cache
)
from gwml2.utilities import temp_disconnect_signal, make_aware_local

User = get_user_model()


class HarvestingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BaseHarvester(ABC):
    """ Abstract class for harvester """
    attributes = {}
    countries = []
    current_original_id_key = 'current-original-id'

    # This is indicator if we process the station
    is_processing_station = True

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):

        # Other attributes
        self.unit_m = Unit.objects.get(name='m')
        self.replace = replace
        self.original_id = original_id
        self.harvester = harvester
        for attribute in harvester.harvesterattribute_set.all():
            self.attributes[attribute.name] = attribute.value
        self.parameters = HarvesterParameterMap.get_json(harvester)

        # check if it is already run
        self.harvester.refresh_from_db()
        if self.harvester.is_run:
            return
        if self.harvester.harvesterlog_set.filter(
                status=RUNNING
        ).first():
            return

        # Check last code
        self.current_original_id = self.attributes.get(
            self.current_original_id_key, None
        )

        # If it has current original id, we don't process station
        # Until we found the correct one
        # This is for resume process
        if self.current_original_id:
            self.is_processing_station = False
        else:
            self.is_processing_station = True

        self.harvester.is_run = True
        self.harvester.save()
        self.log = HarvesterLog.objects.create(harvester=harvester)

        # run the process
        try:
            with temp_disconnect_signal(
                    signal=post_save,
                    receiver=post_save_measurement,
                    sender=WellLevelMeasurement
            ):
                with temp_disconnect_signal(
                        signal=post_save,
                        receiver=post_save_measurement,
                        sender=WellYieldMeasurement
                ):
                    with temp_disconnect_signal(
                            signal=post_save,
                            receiver=post_save_measurement,
                            sender=WellQualityMeasurement
                    ):
                        self._process()

                        # Run organisation caches
                        self._update('Run organisation caches')
                        generate_data_organisation_cache(
                            self.harvester.organisation.id
                        )

                        # Run country caches
                        self._update('Run country caches')
                        countries = list(set(self.countries))
                        for country in countries:
                            generate_data_country_cache(country)

                        self._done('Done')

                        # RUN MATERIALIZED VIEW
                        running = Harvester.objects.filter(is_run=True).first()
                        if not running:
                            MaterializedViewWell.refresh()

                        # Delete current original id attribute
                        self.delete_attribute(self.current_original_id_key)
        except HarvestingError as e:
            self._error(f'{e}')
        except Exception:
            self._error(traceback.format_exc())

        # Make the task id non
        harvester.task_id = None
        harvester.save()

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
        self.log.save(update_fields=['end_time', 'status', 'note'])
        print(self.log.note)

    def _done(self, message=''):
        self.harvester.is_run = False
        self.harvester.save()
        self.log.end_time = timezone.now()
        self.log.status = DONE
        self.log.note = message
        self.log.save(update_fields=['end_time', 'status', 'note'])

    def _update(self, message=''):
        """ Update note for the log """
        self.log.note = message
        self.log.save(update_fields=['note'])
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

    def check_current_well(self, original_id):
        """Check current well."""
        # If not process station but the original id is same with current one
        # make process station true
        if not self.is_processing_station and original_id == self.current_original_id:
            self.is_processing_station = True

        # Save current original id
        if self.is_processing_station:
            self.update_attribute(
                self.current_original_id_key, original_id
            )

    def _save_well(
            self,
            original_id: str,
            name: str,
            latitude: float,
            longitude: float,
            feature_type: typing.Optional[TermFeatureType] = None,
            ground_surface_elevation_masl: typing.Optional[float] = None,
            top_of_well_elevation_masl: typing.Optional[float] = None,
            description: typing.Optional[str] = None,
            reassign_organisation=False
    ) -> Well:
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

        if reassign_organisation:
            if well.organisation != self.harvester.organisation:
                well.organisation = self.harvester.organisation
                well.save()

        # If not process station but the original id is same with current one
        # make process station true
        if not self.is_processing_station and well.original_id == self.current_original_id:
            self.is_processing_station = True

        # Save current original id
        if self.is_processing_station:
            self.update_attribute(
                self.current_original_id_key, well.original_id
            )

        return well

    def _save_measurement(
            self,
            model: typing.Union[
                WellLevelMeasurement, WellQualityMeasurement,
                WellYieldMeasurement
            ],
            time: datetime,
            defaults: dict,
            well: Well,
            value: float = None,
            unit: Unit = None
    ):
        """ Save measurement """
        try:
            obj, created = model.objects.get_or_create(
                well=well,
                parameter=defaults.get('parameter', None),
                time=make_aware_local(time),
                defaults=defaults
            )
        except (
                WellLevelMeasurement.MultipleObjectsReturned,
                WellQualityMeasurement.MultipleObjectsReturned,
                WellYieldMeasurement.MultipleObjectsReturned,
        ):
            obj = model.objects.filter(
                well=well,
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

    def post_processing_well(self, well: Well):
        """Specifically for processing cache after procesing well."""
        import time
        from gwml2.utils.generate_dem_well_value import (
            assign_glo_90m_elevation_for_well
        )
        original_id = well.original_id
        t_start = time.time()
        well.update_metadata()

        self._update(f'Generate DEM for {original_id}')
        assign_glo_90m_elevation_for_well(well)

        self._update(f'Generate data well cache for {original_id}')
        generate_data_well_cache(
            well.id,
            generate_country_cache=False,
            generate_organisation_cache=False
        )

        self._update(f'Run quality control for {original_id}')
        well.quality_control.run()

        if well.country:
            self.countries.append(well.country.code)

        self._update(
            f'post_processing_well done in {time.time() - t_start:.2f}s'
            f' for {well.original_id}'
        )

    def update_attribute(self, key: str, value):
        """Update attribute."""
        attr, _ = HarvesterAttribute.objects.get_or_create(
            harvester=self.harvester,
            name=key
        )
        attr.value = value
        attr.save()

    def delete_attribute(self, key: str):
        """Update attribute."""
        attr, _ = HarvesterAttribute.objects.get_or_create(
            harvester=self.harvester,
            name=key
        )
        attr.delete()
