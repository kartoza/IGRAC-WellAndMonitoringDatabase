import zipfile

from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from lxml import etree

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

    # ------------------------------------
    # Script to read ods file
    # ------------------------------------
    @staticmethod
    def get_data(file_path):
        records = {}
        with zipfile.ZipFile(file_path, "r") as zf:
            with zf.open("content.xml") as xml_file:
                context = etree.iterparse(
                    xml_file, events=("start", "end"), huge_tree=True,
                    recover=True
                )
                namespace = {
                    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}

                current_sheet = None
                current_sheet_data = []
                for event, elem in context:
                    if event == "start" and elem.tag.endswith("table"):
                        if current_sheet:
                            records[current_sheet] = current_sheet_data

                        current_sheet = elem.attrib.get(
                            '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name',
                            'Unknown Sheet'
                        )
                        current_sheet_data = []

                    if event == "end" and elem.tag.endswith("table-row"):
                        row_data = []
                        for cell in elem.xpath(
                                './/table:table-cell', namespaces=namespace
                        ):
                            spanned = int(
                                cell.attrib.get(
                                    '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-spanned',
                                    '1'
                                )
                            )
                            repeated = int(
                                cell.attrib.get(
                                    '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated',
                                    '1'
                                )
                            )

                            # Extract cell value
                            cell_value = cell.xpath(
                                './/text:p/text()',
                                namespaces={
                                    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                                }
                            )
                            if not cell_value:
                                value_type = cell.attrib.get(
                                    'office:value-type')
                                if value_type == 'float':
                                    cell_value = [
                                        cell.attrib.get('office:value')
                                    ]
                                elif value_type == 'date':
                                    cell_value = [
                                        cell.attrib.get('office:date-value')
                                    ]

                            cell_content = ' '.join(
                                cell_value
                            ) if cell_value else ''

                            # Create empty data
                            for _ in range(spanned * repeated):
                                if _ == 0:
                                    row_data.append(cell_content)
                                else:
                                    row_data.append('')

                        # Append to current sheet data
                        try:
                            if row_data[0]:
                                current_sheet_data.append(row_data)
                        except IndexError:
                            pass

                        # Free memory
                        elem.clear()

                # For the last sheet
                if current_sheet:
                    records[current_sheet] = current_sheet_data
                return records

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
            records = BatchUploader.get_data(_file.path)

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
                restart, well_by_id, relation_cache,
                file_path=upload_session.upload_file.path
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
