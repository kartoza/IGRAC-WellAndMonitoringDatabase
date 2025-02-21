"""Test ODS Reader."""
import json
from unittest.mock import patch

from core.settings.utils import absolute_path
from gwml2.models.upload_session import UploadSession
from gwml2.tasks.uploader import (
    GeneralInformationUploader,
    HydrogeologyUploader,
    ManagementUploader,
    MonitoringDataUploader
)
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.tests.base import GWML2Test
from gwml2.utils.ods_reader import get_count
from gwml2.utils.template_check import ExcelOutOfDate

captured_data = {}


class ODSReaderTest(GWML2Test):
    """Test ODS Reader."""

    def _convert_record(self, sheet_name, record):
        """ convert record into json data
        :return: dictionary of forms
        :rtype: dict
        """
        try:
            captured_data[sheet_name].append(record)
        except KeyError:
            captured_data[sheet_name] = [record]
        raise Exception('Error')

    def test_count(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.old.ods')
        self.assertEquals(get_count(file_path, 'General_Information'), 2)
        self.assertEquals(get_count(file_path, 'General Information'), 2)
        self.assertEquals(get_count(file_path, 'General'), None)
        self.assertEquals(get_count(file_path, 'Hydrogeology'), 2)
        self.assertEquals(get_count(file_path, 'Management'), 2)

    def test_sheet_not_found(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.old.ods')
        upload_session = UploadSession.objects.create()
        with self.assertRaises(KeyError) as e:
            MonitoringDataUploader(
                upload_session, {}, 0, 1,
                file_path=file_path
            )
            self.assertEquals(
                f'{e}',
                "'Sheet Groundwater Level in excel is not found. "
                "This sheet is used by Monitoring Data. "
                "Please check if you use the correct uploader/tab. '"
            )

    def test_sheet_old_version(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.old.ods')
        upload_session = UploadSession.objects.create()
        with self.assertRaises(ExcelOutOfDate) as e:
            GeneralInformationUploader(
                upload_session, {}, 0, 1,
                file_path=file_path
            )
            self.assertEquals(
                f'{e}',
                "The file is out of date, "
                "please download the latest template on the form"
            )

    @patch.object(BaseUploader, "_convert_record", new=_convert_record)
    def test_script(self):
        """To file exist."""
        try:
            del captured_data['General Information']
            del captured_data['Hydrogeology']
            del captured_data['Management']
        except KeyError:
            pass
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.ods')
        GeneralInformationUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        HydrogeologyUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        ManagementUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.assertEquals(
            captured_data['General Information'][0][:20],
            [
                '1', 'AA', 'Water well', 'Observation / monitoring',
                '', '', '-36.338', '174.74365',
                '', '', '', '', '', '', 'Indonesia',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            captured_data['General Information'][1][:20],
            [
                '2', 'AB', 'Water well', 'Observation / monitoring',
                '', '', '-36.351', '174.75797',
                '', '', '', '', '', '', 'Indonesia',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            captured_data['Hydrogeology'][0][:14],
            [
                '1', 'Test 1', 'Material 1', 'Sand and gravel', '',
                'Confined',
                '', '', '', '', '', '',
                '2', '1/m'
            ],
        )
        self.assertEquals(
            captured_data['Hydrogeology'][1][:14],
            [
                '2', 'Test 2', 'Material 2', 'Sandstone', '',
                'Unconfined',
                '', '', '', '', '', '',
                '3', '1/m'
            ],
        )
        self.assertEquals(
            captured_data['Management'][0][:10],
            [
                '1', 'Organisation 1', '', '', 'Domestic',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            captured_data['Management'][1][:10],
            [
                '2', 'Organisation 2', '', '', 'Irrigation',
                '', '', '', '', ''
            ]
        )

    @patch.object(BaseUploader, "_convert_record", new=_convert_record)
    def test_resumed(self):
        """To file exist."""
        try:
            del captured_data['General Information']
            del captured_data['Hydrogeology']
            del captured_data['Management']
        except KeyError:
            pass
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.ods')
        status = {
            'General Information': {
                'added': 1, 'error': 0, 'skipped': 0
            },
            'Hydrogeology': {
                'added': 1, 'error': 0, 'skipped': 0
            },
            'Management': {
                'added': 1, 'error': 0, 'skipped': 0
            }
        }
        GeneralInformationUploader(
            UploadSession.objects.create(status=json.dumps(status)), 0, 1,
            file_path=file_path
        )
        HydrogeologyUploader(
            UploadSession.objects.create(status=json.dumps(status)), 0, 1,
            file_path=file_path
        )
        ManagementUploader(
            UploadSession.objects.create(status=json.dumps(status)), 0, 1,
            file_path=file_path
        )
        self.assertEquals(
            captured_data['General Information'][0][:20],
            [
                '2', 'AB', 'Water well', 'Observation / monitoring',
                '', '', '-36.351', '174.75797',
                '', '', '', '', '', '', 'Indonesia',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            captured_data['Hydrogeology'][0][:14],
            [
                '2', 'Test 2', 'Material 2', 'Sandstone', '',
                'Unconfined',
                '', '', '', '', '', '',
                '3', '1/m'
            ],
        )
        self.assertEquals(
            captured_data['Management'][0][:10],
            [
                '2', 'Organisation 2', '', '', 'Irrigation',
                '', '', '', '', ''
            ]
        )
