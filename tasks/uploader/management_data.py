from celery.utils.log import get_task_logger

from gwml2.models.term import TermGroundwaterUse
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class ManagementUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'General Information'
    IS_OPTIONAL = True
    SHEETS = ['Management']

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'name': None,
        'manager': None,
        'description': None,
        'groundwater_use': TermGroundwaterUse,
        'number_of_users': None,
        'number': None,
        'valid_from': None,
        'valid_until': None,
        'license_description': None
    }

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        return {
            "management": {
                "license": {
                    "number": data['number'],
                    "valid_from": data['valid_from'],
                    "valid_until": data['valid_until'],
                    "description": data['license_description']
                },
                "manager": data['manager'],
                "description": data['description'],
                "groundwater_use": data['groundwater_use'],
                "number_of_users": data['number_of_users'],
            }
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        return None
