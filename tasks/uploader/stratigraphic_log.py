from celery.utils.log import get_task_logger

from gwml2.models.general import Unit
from gwml2.models.term import TermReferenceElevationType
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.terms import SheetName

logger = get_task_logger(__name__)


class StratigraphicLogUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'Drilling and construction'
    IS_OPTIONAL = True
    SHEETS = [SheetName.stratigraphic_log]

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'name': None,
        'reference_elevation': TermReferenceElevationType,
        'top_depth_value': None,
        'top_depth_unit': Unit,
        'bottom_depth_value': None,
        'bottom_depth_unit': Unit,
        'material': None,
        'stratigraphic_unit': None
    }
    well_founds = []

    def convert_record(self, sheet_name, data, raw_record: list):
        """ return object that will be used
        """
        return {
            "drilling": {
                "skip_save": True,
                "stratigraphic_log": [
                    {
                        "id": None,
                        "reference_elevation": data['reference_elevation'],
                        "top_depth_value": data['top_depth_value'],
                        "top_depth_unit": data['top_depth_unit'],
                        "bottom_depth_value": data['bottom_depth_value'],
                        "bottom_depth_unit": data['bottom_depth_unit'],
                        "material": data['material'],
                        "stratigraphic_unit": data['stratigraphic_unit'],
                    }
                ]
            }
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        if well.id not in self.well_founds:
            if well.drilling:
                well.drilling.stratigraphiclog_set.all().delete()
            self.well_founds.append(well.id)
        return None
