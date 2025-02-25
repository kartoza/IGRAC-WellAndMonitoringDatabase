"""Test ODS Reader."""
import json
from unittest.mock import patch

from core.settings.utils import absolute_path
from gwml2.models.upload_session import UploadSession
from gwml2.tasks.uploader import (
    GeneralInformationUploader,
    HydrogeologyUploader,
    ManagementUploader,
    MonitoringDataUploader,
    DrillingAndConstructionUploader,
    WaterStrikeUploader,
    StratigraphicLogUploader,
    StructuresUploader
)
from gwml2.tests.base import GWML2Test
from gwml2.utils.ods_reader import get_count
from gwml2.utils.template_check import ExcelOutOfDate

captured_data = {}

data = {
    'General Information': [
        {
            'original_id': "1",
            'name': "AA",
            'feature_type': 'Water well',
            'purpose': "Production",
            'status': "Active",
            'description': "This is AA",
            'latitude': "-36.338",
            'longitude': "174.74365",
            'ground_surface_elevation_value': "1",
            'ground_surface_elevation_unit': "m",
            'glo_90m_elevation_value': "2",
            'glo_90m_elevation_unit': "m",
            'top_borehole_elevation_value': "3",
            'top_borehole_elevation_unit': "ft",
            'country': "Indonesia",
            'address': "Address of AA",
            'license_type': "License A",
            'license_restriction': "Restriction A",
            'is_groundwater_level': "Yes",
            'is_groundwater_quality': "No"
        },
        {
            'original_id': "2",
            'name': "AB",
            'feature_type': "Water well",
            'purpose': "Observation / monitoring",
            'status': "Dry",
            'description': "This is AB",
            'latitude': "-36.351",
            'longitude': "174.75797",
            'ground_surface_elevation_value': "2",
            'ground_surface_elevation_unit': "m",
            'glo_90m_elevation_value': "3",
            'glo_90m_elevation_unit': "m",
            'top_borehole_elevation_value': "4",
            'top_borehole_elevation_unit': "ft",
            'country': "Indonesia",
            'address': "Address of AB",
            'license_type': "License B",
            'license_restriction': "Restriction B",
            'is_groundwater_level': "No",
            'is_groundwater_quality': "Yes"
        }
    ],
    'Hydrogeology': [
        {
            'original_id': "1",
            'name': 'AA',
            'aquifer_name': "Test 1",
            'aquifer_material': "Material 1",
            'aquifer_type': "Sand and gravel",
            'aquifer_thickness': "1",
            'confinement': "Confined",
            'degree_of_confinement': "2",
            'porosity': "3",
            'hydraulic_conductivity_value': "5",
            'hydraulic_conductivity_unit': "m/day",
            'transmissivity_value': "6",
            'transmissivity_unit': "m/day",
            'specific_storage_value': "2",
            'specific_storage_unit': "1/m",
            'specific_capacity_value': "4",
            'specific_capacity_unit': "m/day",
            'storativity_value': "8",
            'storativity_unit': "m³/min",
            'test_type': "Test type 1",
        },
        {
            'original_id': "2",
            'name': 'AB',
            'aquifer_name': "Test 2",
            'aquifer_material': "Material 2",
            'aquifer_type': "Sandstone",
            'aquifer_thickness': "2",
            'confinement': "Unconfined",
            'degree_of_confinement': "3",
            'porosity': "4",
            'hydraulic_conductivity_value': "6",
            'hydraulic_conductivity_unit': "m/day",
            'transmissivity_value': "7",
            'transmissivity_unit': "m/day",
            'specific_storage_value': "3",
            'specific_storage_unit': "1/m",
            'specific_capacity_value': "5",
            'specific_capacity_unit': "m/day",
            'storativity_value': "9",
            'storativity_unit': "m³/s",
            'test_type': "Test type 2",
        }
    ],
    'Management': [
        {
            'original_id': "1",
            'well_name': "AA",
            'name': "Organisation 1",
            'manager': "Owner 1",
            'description': "Description 1",
            'groundwater_use': "Domestic",
            'number_of_users': "1",
            'number': "A",
            'valid_from': "2020-01-01",
            'valid_until': "2020-12-31",
            'license_description': "License 1"
        },
        {
            'original_id': "2",
            'well_name': "AB",
            'name': "Organisation 2",
            'manager': "Owner 2",
            'description': "Description 2",
            'groundwater_use': "Irrigation",
            'number_of_users': "2",
            'number': "B",
            'valid_from': "2021-01-01",
            'valid_until': "2021-12-31",
            'license_description': "License 2"
        }
    ],
    'Drilling': [
        {
            'original_id': "1",
            'name': 'AA',
            'total_depth_value': "1",
            'total_depth_unit': "m",
            'drilling_method': "Auger drilling",
            'driller': "Driller 1",
            'successful': "Yes",
            'cause_of_failure': "Failure 1",
            'year_of_drilling': "2020",
            'pump_installer': "Pump 1",
            'pump_description': "Description 1",
        },
        {
            'original_id': "2",
            'name': 'AB',
            'total_depth_value': "2",
            'total_depth_unit': "ft",
            'drilling_method': "Cable tool drilling",
            'driller': "Driller 2",
            'successful': "No",
            'cause_of_failure': "Failure 2",
            'year_of_drilling': "2021",
            'pump_installer': "Pump 2",
            'pump_description': "Description 2",
        }
    ],
    'Water Strike': [
        {
            'original_id': "1",
            'name': "AA",
            'depth_value': "1",
            'depth_unit': "m",
            'reference_elevation': "Top of borehole",
            'description': "Description 1",
        },
        {
            'original_id': "2",
            'name': "AB",
            'depth_value': "2",
            'depth_unit': "ft",
            'reference_elevation': "Ground surface level ASL",
            'description': "Description 2",
        }
    ],
    'Stratigraphic Log': [
        {
            'original_id': "1",
            'name': "AA",
            'reference_elevation': "Top of borehole",
            'top_depth_value': "1",
            'top_depth_unit': "m",
            'bottom_depth_value': "3",
            'bottom_depth_unit': "ft",
            'material': "Material 1",
            'stratigraphic_unit': "Stratigraphic unit 1"
        },
        {
            'original_id': "2",
            'name': "AB",
            'reference_elevation': "Ground surface level ASL",
            'top_depth_value': "2",
            'top_depth_unit': "ft",
            'bottom_depth_value': "4",
            'bottom_depth_unit': "m",
            'material': "Material 2",
            'stratigraphic_unit': "Stratigraphic unit 2"
        }
    ],
    'Construction': [
        {
            'original_id': "1",
            'name': "AA",
            'type': "Casing",
            'reference_elevation': "Top of borehole",
            'top_depth_value': "1",
            'top_depth_unit': "m",
            'bottom_depth_value': "3",
            'bottom_depth_unit': "ft",
            'diameter_value': "5",
            'diameter_unit': "cm",
            'material': "Material 1",
            'description': "Description 1"
        },
        {
            'original_id': "2",
            'name': "AB",
            'type': "Screen",
            'reference_elevation': "Ground surface level ASL",
            'top_depth_value': "2",
            'top_depth_unit': "ft",
            'bottom_depth_value': "4",
            'bottom_depth_unit': "m",
            'diameter_value': "6",
            'diameter_unit': "ft",
            'material': "Material 2",
            'description': "Description 2"
        }
    ],
    'Groundwater Level': [
        {
            'original_id': "1",
            'name': "AA",
            'time': "2020-01-01 00:00:00",
            'parameter': "Water depth [from the ground surface]",
            'value_value': "1",
            'value_unit': "m",
            'methodology': "Methodology 1"
        },
        {
            'original_id': "2",
            'name': "AB",
            'time': "2021-01-01 00:00:00",
            'parameter': "Water level elevation a.m.s.l.",
            'value_value': "2",
            'value_unit': "ft",
            'methodology': "Methodology 2"
        }
    ],
    'Groundwater Quality': [
        {
            'original_id': "1",
            'name': "AA",
            'time': "2020-01-01 00:00:00",
            'parameter': "EC",
            'value_value': "1",
            'value_unit': "S/m",
            'methodology': "Methodology 3"
        },
        {
            'original_id': "2",
            'name': "AB",
            'time': "2021-01-01 00:00:00",
            'parameter': "pH",
            'value_value': "2",
            'value_unit': "",
            'methodology': "Methodology 4"
        }
    ],
    'Abstraction-Discharge': [
        {
            'original_id': "1",
            'name': "AA",
            'time': "2020-01-01 00:00:00",
            'parameter': "Abstraction",
            'value_value': "1",
            'value_unit': "m³/h",
            'methodology': "Methodology 5"
        },
        {
            'original_id': "2",
            'name': "AB",
            'time': "2021-01-01 00:00:00",
            'parameter': "Abstraction",
            'value_value': "2",
            'value_unit': "m³/h",
            'methodology': "Methodology 6"
        }
    ]
}


class ODSReaderTest(GWML2Test):
    """Test ODS Reader."""

    def setUp(self):
        """Set up test data before running each test."""
        from django.core.management import call_command
        call_command("update_fixtures")

    def convert_record(self, sheet_name, record, raw_record):
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
        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.old.ods'
        )
        self.assertEquals(get_count(file_path, 'General_Information'), 2)
        self.assertEquals(get_count(file_path, 'General Information'), 2)
        self.assertEquals(get_count(file_path, 'General'), None)
        self.assertEquals(get_count(file_path, 'Hydrogeology'), 2)
        self.assertEquals(get_count(file_path, 'Management'), 2)

    def test_sheet_not_found(self):
        """To file exist."""
        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.old.ods'
        )
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

    def check_old_file(self, Uploader, file_name):
        """Check old file."""
        upload_session = UploadSession.objects.create()
        with self.assertRaises(ExcelOutOfDate) as e:
            Uploader(
                upload_session, {}, 0, 1,
                file_path=absolute_path(
                    'gwml2', 'tests', 'fixtures', file_name
                )
            )
            self.assertEquals(
                f'{e}',
                "The file is out of date, "
                "please download the latest template on the form"
            )

    def test_sheet_old_version(self):
        """To file exist."""
        self.check_old_file(GeneralInformationUploader, 'wells.old.ods')
        self.check_old_file(HydrogeologyUploader, 'wells.old.ods')
        self.check_old_file(ManagementUploader, 'wells.old.ods')
        self.check_old_file(
            DrillingAndConstructionUploader,
            'drilling_and_construction.old.ods'
        )
        self.check_old_file(
            WaterStrikeUploader, 'drilling_and_construction.old.ods'
        )
        self.check_old_file(
            StratigraphicLogUploader, 'drilling_and_construction.old.ods'
        )
        self.check_old_file(
            StructuresUploader, 'drilling_and_construction.old.ods'
        )
        self.check_old_file(
            MonitoringDataUploader, 'monitoring_data.old.ods'
        )

    def compare(self, source, from_uploader):
        """Compare data."""
        for key, value in source.items():
            if isinstance(from_uploader[key], int):
                self.assertIsNotNone(from_uploader[key])
            else:
                self.assertEqual(value, from_uploader[key])

    @patch.object(
        GeneralInformationUploader, "convert_record", new=convert_record
    )
    @patch.object(HydrogeologyUploader, "convert_record", new=convert_record)
    @patch.object(ManagementUploader, "convert_record", new=convert_record)
    def test_well_file(self):
        """To file exist."""
        for key, value in data.items():
            try:
                del captured_data[key]
            except KeyError:
                pass

        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'wells.ods')

        # General information
        GeneralInformationUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['General Information'][0],
            captured_data['General Information'][0]
        )
        self.compare(
            data['General Information'][1],
            captured_data['General Information'][1]
        )

        # Hydrogeology
        HydrogeologyUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Hydrogeology'][0],
            captured_data['Hydrogeology'][0]
        )
        self.compare(
            data['Hydrogeology'][1],
            captured_data['Hydrogeology'][1]
        )

        # Management
        ManagementUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Management'][0],
            captured_data['Management'][0]
        )
        self.compare(
            data['Management'][1],
            captured_data['Management'][1]
        )

    @patch.object(
        DrillingAndConstructionUploader, "convert_record",
        new=convert_record
    )
    @patch.object(
        WaterStrikeUploader, "convert_record",
        new=convert_record
    )
    @patch.object(
        StratigraphicLogUploader, "convert_record",
        new=convert_record
    )
    @patch.object(
        StructuresUploader, "convert_record",
        new=convert_record
    )
    def test_drilling_and_construction_file(self):
        """To file exist."""
        for key, value in data.items():
            try:
                del captured_data[key]
            except KeyError:
                pass
        # DRILLING AND CONSTRUCTION
        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'drilling_and_construction.ods'
        )
        # drilling and construction
        DrillingAndConstructionUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Drilling'][0],
            captured_data['Drilling'][0]
        )
        self.compare(
            data['Drilling'][1],
            captured_data['Drilling'][1]
        )
        # Water strike
        WaterStrikeUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Water Strike'][0],
            captured_data['Water Strike'][0]
        )
        self.compare(
            data['Water Strike'][1],
            captured_data['Water Strike'][1]
        )
        # Stratigraphic Log
        StratigraphicLogUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Stratigraphic Log'][0],
            captured_data['Stratigraphic Log'][0]
        )
        self.compare(
            data['Stratigraphic Log'][1],
            captured_data['Stratigraphic Log'][1]
        )
        # Construction
        StructuresUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Construction'][0],
            captured_data['Construction'][0]
        )
        self.compare(
            data['Construction'][1],
            captured_data['Construction'][1]
        )

    @patch.object(
        MonitoringDataUploader, "convert_record",
        new=convert_record
    )
    def test_monitoring_data_file(self):
        """To file exist."""
        for key, value in data.items():
            try:
                del captured_data[key]
            except KeyError:
                pass
        # DRILLING AND CONSTRUCTION
        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'monitoring_data.ods'
        )
        # Groundwater Level
        MonitoringDataUploader(
            UploadSession.objects.create(), 0, 1,
            file_path=file_path
        )
        self.compare(
            data['Groundwater Level'][0],
            captured_data['Groundwater Level'][0]
        )
        self.compare(
            data['Groundwater Level'][1],
            captured_data['Groundwater Level'][1]
        )
        # Groundwater Quality
        self.compare(
            data['Groundwater Quality'][0],
            captured_data['Groundwater Quality'][0]
        )
        self.compare(
            data['Groundwater Quality'][1],
            captured_data['Groundwater Quality'][1]
        )
        # Abstraction-Discharge
        self.compare(
            data['Abstraction-Discharge'][0],
            captured_data['Abstraction-Discharge'][0]
        )
        self.compare(
            data['Abstraction-Discharge'][1],
            captured_data['Abstraction-Discharge'][1]
        )

    @patch.object(
        GeneralInformationUploader, "convert_record", new=convert_record
    )
    @patch.object(HydrogeologyUploader, "convert_record", new=convert_record)
    @patch.object(ManagementUploader, "convert_record", new=convert_record)
    def test_resumed(self):
        """To file exist."""
        for key, value in data.items():
            try:
                del captured_data[key]
            except KeyError:
                pass

        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'wells.ods')
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
        self.compare(
            data['General Information'][1],
            captured_data['General Information'][0]
        )
        self.compare(
            data['Hydrogeology'][1],
            captured_data['Hydrogeology'][0]
        )
        self.compare(
            data['Management'][1],
            captured_data['Management'][0]
        )
