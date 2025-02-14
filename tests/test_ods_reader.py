"""Test ODS Reader."""

from core.settings.utils import absolute_path
from gwml2.tasks.uploader.uploader import BatchUploader
from gwml2.tests.base import GWML2Test


class ODSReaderTest(GWML2Test):
    """Test ODS Reader."""

    def test_script(self):
        """To file exist."""
        file_path = absolute_path('gwml2', 'tests', 'fixtures', 'test.ods')
        results = BatchUploader.get_data(file_path)
        print(results)
        self.assertEquals(
            results,
            {
                'General_Information': [
                    [
                        'ID', 'Name', 'Feature Type', 'Purpose', 'Status',
                        'Description', 'Latitude', 'Longitude',
                        'Ground surface elevation',
                        'DEM elevation based on the GLO_90m dataset',
                        'Top of well elevation', 'Country', 'Address',
                        'License'
                    ],
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
                        'The address of the data point.', 'License type.',
                        'Restriction.'
                    ],
                    [
                        '1', 'AA', 'Water well', 'Observation / monitoring',
                        None, None, '-36.338', '174.74365', None, 'Indonesia'
                    ],
                    [
                        '2', 'AB', 'Water well', 'Observation / monitoring',
                        None, None'-36.351', '174.75797', None, 'Indonesia'
                    ], [], [], []
                ],
                'Hydrogeology': [
                    [
                        'ID', 'Aquifer Name', 'Aquifer Material',
                        'Aquifer Type',
                        'Aquifer Thickness', 'Confinement',
                        'Degree of confinement', 'Porosity',
                        'Hydraulic Conductivity', 'Transmissivity',
                        'Specific storage', 'Specific capacity', 'Storativity',
                        'Test type'
                    ],
                    [
                        'The original ID of the groundwater point.', None,
                        None,
                        'Value must be either: • Sand and gravel • Sandstone • Carbonate-rock • Sandstone and carbonate-rock • Igneous and metamorphic • Other',
                        None,
                        'Value must be either: • Confined • Semi-confined • Unconfined',
                        None, 'Unit must be either: • m/day', None,
                        'Unit must be either: • m²/day', None,
                        'Unit must be either: • 1/m', None,
                        'Unit must be either: • m²/day', None,
                        'Unit must be either: • m³/day • m³/h • m³/min • m³/s'],
                    [
                        '1', 'Test 1', 'Material 1', 'Sand and gravel', None,
                        'Confined', None, None, '2', '1/m'
                    ],
                    [
                        '2', 'Test 2', 'Material 2', 'Sandstone', None,
                        'Unconfined', None, None, '3', '1/m'], [], [], []
                ],
                'Management': [
                    [
                        'ID', 'Organisation', 'Groundwater use',
                        'Number of people served', 'License'
                    ],
                    [
                        'The original ID of the groundwater point.',
                        'Name', 'Manager / owner', 'Description',
                        'Unit must be either:  Domestic  Irrigation  Livestock  Industrial  Services (e.g. tourism)',
                        None, 'Number', 'Valid from (yyyy-mm-dd )',
                        'Valid until (yyyy-mm-dd)', 'Description'
                    ],
                    [
                        '1', 'Organisation 1', None, None, 'Domestic'
                    ],
                    [
                        '2', 'Organisation 2', None, None, 'Irrigation'
                    ], [], [], []
                ]
            }

        )
