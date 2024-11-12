from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from pyexcel_ods3 import get_data

from gwml2.models.upload_session import (
    UploadSession, UploadSessionCancelled
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


class BatchUploader:
    """Batch uploader for multiple uploader."""

    def __init__(
            self, upload_session: UploadSession,
            uploaders: list, restart: bool = False
    ):

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
                        self.process(upload_session, uploaders, restart)
                    except UploadSessionCancelled:
                        self.upload_session.update_step('Create report')
                        self.upload_session.create_report_excel()
                        self.upload_session.update_step('Cancelled')
                        return

    def process(
            self, upload_session: UploadSession, uploaders: list,
            restart: bool = False
    ):
        """Process."""
        self.upload_session = upload_session

        if restart:
            self.upload_session.status = ''
            self.upload_session.save()

        # READ FILE
        records = {}
        self.upload_session.update_step('Reading file', progress=1)
        _file = self.upload_session.upload_file
        if _file:
            _file.seek(0)
            records = get_data(_file.path)
            if not records:
                error = 'No data found.'
                self.upload_session.update_progress(
                    finished=True,
                    progress=100,
                    status=error
                )
                return

        # ------------------------------------
        # Run upload
        # ------------------------------------
        relation_cache = {}
        well_by_id = {}
        min_progress = 5
        interval_progress = 65 / len(uploaders)
        self.upload_session.update_step('Upload data', min_progress)
        for idx, Uploader in enumerate(uploaders):
            Uploader(
                upload_session, records,
                min_progress, interval_progress,
                restart, well_by_id, relation_cache
            )
            min_progress += interval_progress

        # ------------------------------------
        # Run the data cache
        # ------------------------------------
        self.upload_session.update_step('Running wells cache', 70)
        wells_id = list(
            self.upload_session.uploadsessionrowstatus_set.filter(
                well__isnull=False,
                status=0,
            ).values_list(
                'well_id', flat=True
            )
        )
        wells_id = list(set(wells_id))
        count = len(wells_id)
        for index, well_id in enumerate(wells_id):
            process_percent = ((index / count) * 10) + 70
            self.upload_session.update_step(
                f'Running {count} wells cache',
                progress=int(process_percent)
            )
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

        # ------------------------------------
        # Run the country cache
        # ------------------------------------
        self.upload_session.update_step('Running country cache', 80)
        countries_code = list(
            Well.objects.filter(
                id__in=wells_id
            ).values_list('country__code', flat=True)
        )
        countries_code = list(set(countries_code))
        count = len(countries_code)
        for index, country_code in enumerate(countries_code):
            process_percent = ((index / count) * 5) + 80
            self.upload_session.update_step(
                'Running country cache',
                progress=int(process_percent)
            )
            generate_data_country_cache(country_code)
        # ------------------------------------
        # Run the organisation cache
        # ------------------------------------
        self.upload_session.update_step('Running organisation cache', 85)
        organisation_ids = list(
            Well.objects.filter(
                id__in=wells_id
            ).values_list('organisation__id', flat=True)
        )
        organisation_ids = list(set(organisation_ids))
        count = len(organisation_ids)
        for index, organisation_id in enumerate(organisation_ids):
            process_percent = ((index / count) * 5) + 85
            self.upload_session.update_step(
                'Running organisation cache',
                progress=int(process_percent)
            )
            generate_data_organisation_cache(organisation_id=organisation_id)

        # ------------------------------------
        # Run the istsos cache for getcapabilities
        # ------------------------------------
        self.upload_session.update_step('Running istsos cache', 90)
        cache_istsos.delay()

        # -----------------------------------------
        # FINISH
        # For report
        self.upload_session.update_step('Create report', 95)
        self.upload_session.create_report_excel()

        # Finish
        self.upload_session.update_step('Finish', 100)
        self.upload_session.update_progress(
            finished=True,
            progress=100
        )
