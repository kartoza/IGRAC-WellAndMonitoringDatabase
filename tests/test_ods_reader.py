"""Test ODS Reader."""

from unittest.mock import patch

from core.settings.utils import absolute_path
from gwml2.models.upload_session import UploadSession
from gwml2.tasks.uploader import (
    GeneralInformationUploader,
    HydrogeologyUploader,
    ManagementUploader
)
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.tasks.uploader.uploader import BatchUploader
from gwml2.tests.base import GWML2Test
from gwml2.utils.template_check import get_records

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

    @patch.object(BaseUploader, "_convert_record", new=_convert_record)
    def test_script_error(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.old.ods')
        results = BatchUploader.get_data(file_path)
        with self.assertRaises(ValueError):
            get_records(
                results.keys(), results, 'General Information'
            )

    @patch.object(BaseUploader, "_convert_record", new=_convert_record)
    def test_script(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.ods')
        results = BatchUploader.get_data(file_path)
        get_records(
            results.keys(), results, 'General Information'
        )
        GeneralInformationUploader(
            UploadSession.objects.create(), results, 0, 1
        )
        HydrogeologyUploader(
            UploadSession.objects.create(), results, 0, 1
        )
        ManagementUploader(
            UploadSession.objects.create(), results, 0, 1
        )
        print(captured_data)
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
