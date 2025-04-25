from celery.utils.log import get_task_logger
from django.db.models.signals import post_save

from gwml2.models.upload_session import (
    UploadSession, UploadSessionCancelled, UploadSessionCheckpoint,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
)
from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement
)
from gwml2.signals.well import post_save_measurement_for_cache
from gwml2.tasks.data_file_cache import generate_data_well_cache
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.data_file_cache.organisation_cache import (
    generate_data_organisation_cache
)
from gwml2.tasks.well import generate_measurement_cache
from gwml2.utilities import temp_disconnect_signal
from igrac_api.tasks.cache_istsos import cache_istsos

logger = get_task_logger(__name__)


class TermNotFound(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class StepCheckpoint:
    """Step checkpoint for upload session."""
    skip = False

    def __init__(self, step_name, upload_session: UploadSession):
        """Initialise the checkpoint."""
        self.step_name = step_name
        self.step_checkpoint = UploadSessionCheckpoint.get_index(step_name)
        self.upload_session = upload_session

    def __enter__(self):
        """Checkpoint function enter."""
        if self.step_checkpoint < self.upload_session.checkpoint:
            self.skip = True
            return self

        # This is when the checkpoint changed
        # Emptying checkpoint ids
        if self.upload_session.checkpoint != self.step_checkpoint:
            self.upload_session.checkpoint_ids = []
        self.upload_session.checkpoint = self.step_checkpoint
        self.upload_session.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class BatchUploader:
    """Batch uploader for multiple uploader."""

    def __init__(
            self,
            upload_session: UploadSession,
            uploaders: list,
            restart: bool = False
    ):
        self.upload_session = upload_session
        self.uploaders = uploaders
        self.restart = restart

        # Disconnect
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
                    try:
                        self.process()
                    except UploadSessionCancelled:
                        self.upload_session.update_step('Create report')
                        self.upload_session.create_report_excel()
                        self.upload_session.update_step('Cancelled')
                        return
                    except Exception as error:
                        self.upload_session.update_progress(
                            finished=True,
                            progress=100,
                            status=str(error)
                        )
                        return

    def saving_data(self):
        """Saving data.

        # ------------------------------------
        # 1. Saving data
        # ------------------------------------
        """
        restart = self.restart
        uploaders = self.uploaders
        upload_session = self.upload_session

        # ------------------------------------
        # Run upload
        # ------------------------------------
        # 1. Saving data
        # ------------------------------------
        relation_cache = {}
        well_by_id = {}
        min_progress = 5
        interval_progress = 65 / len(uploaders)
        self.upload_session.update_step('Reading data', min_progress)
        for idx, Uploader in enumerate(uploaders):
            Uploader(
                upload_session,
                min_progress, interval_progress,
                restart, well_by_id, relation_cache,
                file_path=upload_session.upload_file.path
            )
            min_progress += interval_progress

    def cache_well_data(self, well_id):
        """Cache well data."""
        # This is specifically for cache well data
        if (
                self.upload_session.category ==
                UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
        ):
            generate_measurement_cache(
                well_id=well_id, model=WellLevelMeasurement.__name__
            )
            generate_measurement_cache(
                well_id=well_id, model=WellYieldMeasurement.__name__
            )
            generate_measurement_cache(
                well_id=well_id, model=WellQualityMeasurement.__name__
            )

        generate_data_well_cache(
            well_id=well_id, generate_country_cache=False,
            generate_organisation_cache=False
        )
        well = Well.objects.get(id=well_id)
        well.update_metadata()
        well.save()

    def cache_wells_data(self, wells_id):
        """Cache wells data.

        # ------------------------------------
        # 2. Cache wells data
        # ------------------------------------
        """
        self.upload_session.update_step('Running wells cache', 70)
        checkpoint_ids = self.upload_session.checkpoint_ids
        if not checkpoint_ids:
            checkpoint_ids = []

        wells_id = list(set(wells_id))
        wells_id.sort()
        count = len(wells_id)
        for index, well_id in enumerate(wells_id):
            try:
                well = Well.objects.get(id=well_id)
                process_percent = ((index / count) * 10) + 70
                self.upload_session.update_step(
                    f'{index} / {count} Running cache for {well.name}',
                    progress=int(process_percent)
                )
                if well_id in checkpoint_ids:
                    continue
                self.cache_well_data(well_id)
                self.upload_session.append_checkout_ids(well_id)
            except Well.DoesNotExist:
                pass

    def cache_countries_data(self, wells_id):
        """Cache countries data.

        # ------------------------------------
        # 3. Cache countries data
        # ------------------------------------
        """
        self.upload_session.update_step('Running country cache', 80)
        checkpoint_ids = self.upload_session.checkpoint_ids
        if not checkpoint_ids:
            checkpoint_ids = []

        countries_code = list(
            Well.objects.filter(
                id__in=wells_id,
                country__isnull=False
            ).values_list(
                'country__code', flat=True
            )
        )
        countries_code = list(set(countries_code))
        countries_code.sort()
        count = len(countries_code)
        for index, country_code in enumerate(countries_code):
            process_percent = ((index / count) * 5) + 80
            self.upload_session.update_step(
                f'Running country cache : {countries_code}',
                progress=int(process_percent)
            )

            if country_code in checkpoint_ids:
                continue
            generate_data_country_cache(country_code)
            self.upload_session.append_checkout_ids(country_code)

    def run_istsos_cache(self):
        """Run istsos cache.

        # ------------------------------------
        # 7. Run the istsos cache for getCapabilities
        # ------------------------------------
        """
        cache_istsos.delay()

    def process(self):
        """Process."""
        if self.restart:
            self.upload_session.status = ''
            self.upload_session.checkpoint = (
                UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.SAVING_DATA
                )
            )
            self.upload_session.progress = 0
            self.upload_session.step = ''
            self.upload_session.save()

        # ------------------------------------
        # 1. Saving data
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.SAVING_DATA,
                upload_session=self.upload_session
        ) as checkpoint:
            if not checkpoint.skip:
                self.saving_data()

        # Get the wells id that being saved
        wells_id = list(
            self.upload_session.uploadsessionrowstatus_set.filter(
                well__isnull=False
            ).filter(status=0).values_list(
                'well_id', flat=True
            ).distinct()
        )
        # ------------------------------------
        # 2. Cache wells data
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.CACHE_WELLS,
                upload_session=self.upload_session
        ) as checkpoint:
            if not checkpoint.skip:
                self.cache_wells_data(wells_id)

        # ------------------------------------
        # 3 Cache country data
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.CACHE_COUNTRY,
                upload_session=self.upload_session
        ) as checkpoint:
            if not checkpoint.skip:
                self.cache_countries_data(wells_id)

        # ------------------------------------
        # 4. Cache organisation data
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.CACHE_ORGANISATION,
                upload_session=self.upload_session
        ) as checkpoint:
            if not checkpoint.skip and wells_id:
                self.upload_session.update_step(
                    'Running organisation cache', 85
                )
                generate_data_organisation_cache(
                    organisation_id=self.upload_session.organisation.id
                )

        # ------------------------------------
        # 5. Create report
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.CREATE_REPORT,
                upload_session=self.upload_session
        ) as checkpoint:
            if checkpoint.skip:
                return
            self.upload_session.update_step('Create report', 90)
            self.upload_session.create_report_excel()

        # ------------------------------------
        # 6. Finish
        # ------------------------------------
        with StepCheckpoint(
                UploadSessionCheckpoint.FINISH,
                upload_session=self.upload_session
        ):
            self.upload_session.update_step('Finish', 100)
            self.upload_session.update_progress(
                finished=True,
                progress=100
            )

        # ------------------------------------
        # 7. Run the istsos cache for getCapabilities
        # ------------------------------------
        self.run_istsos_cache()
