from celery.utils.log import get_task_logger

from gwml2.models.general import Unit
from gwml2.models.term import (
    TermReferenceElevationType, TermConstructionStructureType
)
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.terms import SheetName

logger = get_task_logger(__name__)


class StructuresUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'Drilling and construction'
    IS_OPTIONAL = True
    SHEETS = [SheetName.structure]

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'name': None,
        'type': TermConstructionStructureType,
        'reference_elevation': TermReferenceElevationType,
        'top_depth_value': None,
        'top_depth_unit': Unit,
        'bottom_depth_value': None,
        'bottom_depth_unit': Unit,
        'diameter_value': None,
        'diameter_unit': Unit,
        'material': None,
        'description': None
    }
    well_founds = []

    def convert_record(self, sheet_name, data, raw_record: list):
        """ return object that will be used
        """
        return {
            "construction": {
                "skip_save": True,
                "structure": [
                    {
                        "id": None,
                        "type": data['type'],
                        "reference_elevation": data['reference_elevation'],
                        "top_depth_value": data['top_depth_value'],
                        "top_depth_unit": data['top_depth_unit'],
                        "bottom_depth_value": data['bottom_depth_value'],
                        "bottom_depth_unit": data['bottom_depth_unit'],
                        "diameter_value": data['diameter_value'],
                        "diameter_unit": data['diameter_unit'],
                        "material": data['material'],
                        "description": data['description'],
                    }
                ],
            },
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        if well.id not in self.well_founds:
            if well.construction:
                well.construction.constructionstructure_set.all().delete()
            self.well_founds.append(well.id)
        return None
