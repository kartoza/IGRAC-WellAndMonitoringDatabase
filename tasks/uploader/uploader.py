from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
# from pyexcel_ods3 import get_data

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

import zipfile
from lxml import etree
# import json
from decimal import Decimal
from datetime import datetime
# import os
# import shutil

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
    def get_data(self, file_path):
        records = {}

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                content_xml = zip_ref.read('content.xml')
        except KeyError:
            print("Error: 'content.xml' not found in ODS file.")
            return {}

        tree = etree.XML(content_xml)
        namespace = {'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}
        
        for sheet in tree.xpath('//table:table', namespaces=namespace):
            sheet_name = sheet.attrib.get('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name', 'Unknown Sheet')
            print(f"Processing Sheet: {sheet_name}")
            
            sheet_data = []
            headers = []
            
            for row_index, row in enumerate(sheet.xpath('.//table:table-row', namespaces=namespace)):
                row_data = []
                
                for cell in row.xpath('.//table:table-cell', namespaces=namespace):
                    cell_value = cell.xpath('.//text:p/text()', namespaces={'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'})
                    
                    if not cell_value: 
                        value_type = cell.attrib.get('office:value-type')
                        if value_type == 'float':
                            cell_value = [cell.attrib.get('office:value')]
                        elif value_type == 'date':
                            cell_value = [cell.attrib.get('office:date-value')]
                    
                    row_data.append(' '.join(cell_value) if cell_value else None)
                
                while row_data and row_data[-1] is None:
                    row_data.pop()
                
                if row_index == 0:
                    headers = row_data
                else:
                    row_dict = {headers[i]: row_data[i] for i in range(min(len(headers), len(row_data)))}
                    sheet_data.append(row_dict)

            if sheet_data:
                records[sheet_name] = sheet_data

        return records
    
    '''You can use below function to create json file'''

    '''def custom_default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def write_to_json(self, data):
        filename = "monitoring_data.json"
        
        if os.path.exists(filename):
            shutil.copy(filename, filename.replace('.json', '_backup.json'))
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4, default=custom_default)
            print(f"Saved {filename}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False'''

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
            records = self.get_data(_file.path)

            # if records:
            #     write_to_json(records)
            # else:
            #     print("No data found in the ODS file.")
            
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
