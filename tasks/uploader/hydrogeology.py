from celery.utils.log import get_task_logger

from gwml2.models.general import Unit
from gwml2.models.term import TermAquiferType, TermConfinement
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class HydrogeologyUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'General Information'
    IS_OPTIONAL = True
    SHEETS = ['Hydrogeology']

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'aquifer_name': None,
        'aquifer_material': None,
        'aquifer_type': TermAquiferType,
        'aquifer_thickness': None,
        'confinement': TermConfinement,
        'degree_of_confinement': None,
        'porosity': None,
        'hydraulic_conductivity_value': None,
        'hydraulic_conductivity_unit': Unit,
        'transmissivity_value': None,
        'transmissivity_unit': Unit,
        'specific_storage_value': None,
        'specific_storage_unit': Unit,
        'specific_capacity_value': None,
        'specific_capacity_unit': Unit,
        'storativity_value': None,
        'storativity_unit': Unit,
        'test_type': None,
    }

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        return {
            "hydrogeology": {
                "pumping_test": {
                    "porosity": data['porosity'],
                    "hydraulic_conductivity_value": data[
                        'hydraulic_conductivity_value'
                    ],
                    "hydraulic_conductivity_unit": data[
                        'hydraulic_conductivity_unit'
                    ],
                    "transmissivity_value": data['transmissivity_value'],
                    "transmissivity_unit": data['transmissivity_unit'],
                    "specific_storage_value": data['specific_storage_value'],
                    "specific_storage_unit": data['specific_storage_unit'],
                    "specific_capacity_value": data['specific_capacity_value'],
                    "specific_capacity_unit": data['specific_capacity_unit'],
                    "storativity_value": data['storativity_value'],
                    "storativity_unit": data['storativity_unit'],
                    "test_type": data['test_type']
                },
                "aquifer_name": data['aquifer_name'],
                "aquifer_material": data['aquifer_material'],
                "aquifer_type": data['aquifer_type'],
                "aquifer_thickness": data['aquifer_thickness'],
                "confinement": data['confinement'],
            },
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        return None
