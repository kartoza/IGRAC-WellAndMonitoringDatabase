from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get

from gwml2.models.upload_session import UploadSession
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
from gwml2.tasks.well import generate_measurement_cache
from gwml2.utilities import temp_disconnect_signal

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
                    self.process(upload_session, uploaders, restart)

    def process(
            self, upload_session: UploadSession, uploaders: list,
            restart: bool = False
    ):
        """Process."""
        self.upload_session = upload_session

        # READ FILE
        records = {}
        self.upload_session.update_step('Reading file')
        _file = self.upload_session.upload_file
        if _file:
            _file.seek(0)
            records = None
            if str(_file).split('.')[-1] == 'xls':
                records = xls_get(_file, column_limit=20)
            elif str(_file).split('.')[-1] == 'xlsx':
                records = xlsx_get(_file, column_limit=20)
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
                well__isnull=False
            ).values_list(
                'well_id', flat=True
            )
        )
        wells_id = list(set(wells_id))
        count = len(wells_id)
        for index, well_id in enumerate(wells_id):
            process_percent = ((index / count) * 10) + 70
            self.upload_session.update_step(
                'Running wells cache',
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
                well_id=well_id, generate_country_cache=False
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
            process_percent = ((index / count) * 10) + 80
            self.upload_session.update_step(
                'Running country cache',
                progress=int(process_percent)
            )
            generate_data_country_cache(country_code)

        # finish
        self.upload_session.update_progress(
            finished=True,
            progress=100
        )

        # -----------------------------------------
        # FINISH
        # For report
        self.upload_session.update_step('Create report', 90)
        self.upload_session.create_report_excel()

        # Finish
        self.upload_session.update_step('Finish', 100)
        self.upload_session.update_progress(
            finished=True,
            progress=100
        )
