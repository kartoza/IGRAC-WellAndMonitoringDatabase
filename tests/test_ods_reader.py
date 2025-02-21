"""Test ODS Reader."""

from core.settings.utils import absolute_path
from gwml2.tasks.uploader.uploader import BatchUploader
from gwml2.tests.base import GWML2Test
from gwml2.utils.template_check import get_records


class ODSReaderTest(GWML2Test):
    """Test ODS Reader."""

    def test_script_error(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.old.ods')
        results = BatchUploader.get_data(file_path)
        with self.assertRaises(ValueError):
            get_records(
                results.keys(), results, 'General Information'
            )

    def test_script(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.ods')
        results = BatchUploader.get_data(file_path)
        get_records(
            results.keys(), results, 'General Information'
        )
        self.assertEquals(
            results['General_Information'][0][:21],
            [
                'ID', 'Name', 'Feature Type', 'Purpose', 'Status',
                'Description', 'Latitude', 'Longitude',
                'Ground surface elevation', '',
                'DEM elevation based on the GLO_90m dataset', '',
                'Top of well elevation', '', 'Country', 'Address',
                'License', '', 'Measurement Type', '', 'Measurement Data'
            ]
        )
        self.assertEquals(
            results['General_Information'][1][:22],
            [
                'As recorded in the original database.',
                'The name of the data point.',
                'One of the following: • Borehole • Hand-dug well • Spring If the feature type list does not include the type you need, contact the GGIS administrator : ggis@un-igrac.org.',
                'One of the following: • Production • Observation / monitoring • Injection (Managed Aquifer Recharge) • Geothermal energy • Drainage',
                'One of the following: • Active • Dry • Collapsed • Abandoned',
                'A general description of the data point.',
                'Latitude must be expressed in decimal degrees, with a comma for decimal separator.',
                'Longitude must be expressed in decimal degrees, with a comma for decimal separator.',
                'Measured Above Mean Sea Level (AMSL).',
                'Unit must be either:  m  ft',
                'Measured Above Mean Sea Level (AMSL).',
                'Unit must be either:  m  ft',
                'Measured Above Mean Sea Level (AMSL). The top of the well is usually higher than the ground surface elevation.',
                'Unit must be either:  m  ft',
                '3-letters ISO code of the country. See for example: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3#Officially_assigned_code_elements',
                'The address of the data point.',
                'License type.',
                'Restriction.',
                'Groundwater levels: • Yes • No',
                'Groundwater quality: • Yes • No',
                'First Measurement (READ ONLY)',
                'Last Measurement (READ ONLY)'
            ],
        )
        self.assertEquals(
            results['General_Information'][2][:20],
            [
                '1', 'AA', 'Water well', 'Observation / monitoring',
                '', '', '-36.338', '174.74365',
                '', '', '', '', '', '', 'Indonesia',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            results['General_Information'][3][:20],
            [
                '2', 'AB', 'Water well', 'Observation / monitoring',
                '', '', '-36.351', '174.75797',
                '', '', '', '', '', '', 'Indonesia',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            results['Hydrogeology'][0][:19],
            [
                'ID', 'Aquifer Name', 'Aquifer Material',
                'Aquifer Type',
                'Aquifer Thickness', 'Confinement',
                'Degree of confinement', 'Porosity',
                'Hydraulic Conductivity', '', 'Transmissivity', '',
                'Specific storage', '', 'Specific capacity', '',
                'Storativity', '', 'Test type'
            ]
        )
        self.assertEquals(
            results['Hydrogeology'][1][:19],
            [
                'The original ID of the groundwater point.', '', '',
                'Value must be either: • Sand and gravel • Sandstone • Carbonate-rock • Sandstone and carbonate-rock • Igneous and metamorphic • Other',
                '',
                'Value must be either: • Confined • Semi-confined • Unconfined',
                '', '', '',
                'Unit must be either: • m/day', '',
                'Unit must be either: • m²/day', '',
                'Unit must be either: • 1/m', '',
                'Unit must be either: • m²/day', '',
                'Unit must be either: • m³/day • m³/h • m³/min • m³/s', ''
            ],
        )
        self.assertEquals(
            results['Hydrogeology'][2][:14],
            [
                '1', 'Test 1', 'Material 1', 'Sand and gravel', '',
                'Confined',
                '', '', '', '', '', '',
                '2', '1/m'
            ],
        )
        self.assertEquals(
            results['Hydrogeology'][3][:14],
            [
                '2', 'Test 2', 'Material 2', 'Sandstone', '',
                'Unconfined',
                '', '', '', '', '', '',
                '3', '1/m'
            ],
        )
        self.assertEquals(
            results['Management'][0][:10],
            [
                'ID', 'Organisation', '', '', 'Groundwater use',
                'Number of people served', 'License', '', '', '',
            ]
        )
        self.assertEquals(
            results['Management'][1][:10],
            [
                'The original ID of the groundwater point.',
                'Name', 'Manager / owner', 'Description',
                'Unit must be either:  Domestic  Irrigation  Livestock  Industrial  Services (e.g. tourism)',
                '', 'Number', 'Valid from (yyyy-mm-dd )',
                'Valid until (yyyy-mm-dd)', 'Description'
            ]
        )
        self.assertEquals(
            results['Management'][2][:10],
            [
                '1', 'Organisation 1', '', '', 'Domestic',
                '', '', '', '', ''
            ]
        )
        self.assertEquals(
            results['Management'][3][:10],
            [
                '2', 'Organisation 2', '', '', 'Irrigation',
                '', '', '', '', ''
            ]
        )
