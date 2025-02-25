from celery.utils.log import get_task_logger

from gwml2.models.general import Unit
from gwml2.models.term import TermReferenceElevationType
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class WaterStrikeUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'Drilling and construction'
    IS_OPTIONAL = True
    SHEETS = ['Water Strike']

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'name': None,
        'depth_value': None,
        'depth_unit': Unit,
        'reference_elevation': TermReferenceElevationType,
        'description': None,
    }
    well_founds = []

    def convert_record(self, sheet_name, data, raw_record: list):
        """ return object that will be used
        """
        return {
            "drilling": {
                "skip_save": True,
                "water_strike": [
                    {
                        "id": None,
                        "reference_elevation": data['reference_elevation'],
                        "depth_value": data['depth_value'],
                        "depth_unit": data['depth_unit'],
                        "description": data['description']
                    }
                ]
            }
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        if well.id not in self.well_founds:
            if well.drilling:
                well.drilling.waterstrike_set.all().delete()
            self.well_founds.append(well.id)
        return None
