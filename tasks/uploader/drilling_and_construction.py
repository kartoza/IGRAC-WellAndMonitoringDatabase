from celery.utils.log import get_task_logger

from gwml2.models.general import Unit
from gwml2.models.term import TermDrillingMethod
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class DrillingAndConstructionUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'Drilling and construction'
    SHEETS = ['Drilling and Construction']

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'total_depth_value': None,
        'total_depth_unit': Unit,
        'drilling_method': TermDrillingMethod,
        'driller': None,
        'successful': None,
        'cause_of_failure': None,
        'year_of_drilling': None,
        'pump_installer': None,
        'pump_description': None,
    }

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        return {
            "geology": {
                "total_depth_value": data['total_depth_value'],
                "total_depth_unit": data['total_depth_unit']
            },
            "drilling": {
                "drilling_method": data['drilling_method'],
                "driller": data['driller'],
                "successful": data['successful'],
                "cause_of_failure": data['cause_of_failure'],
                "year_of_drilling": data['year_of_drilling'],
            },
            "construction": {
                "pump_installer": data['pump_installer'],
                "pump_description": data['pump_description'],
            },
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        return None
