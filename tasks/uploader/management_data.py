from celery.utils.log import get_task_logger

from gwml2.models.term import TermGroundwaterUse
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.terms import SheetName
from gwml2.utils.well_data import WellData

logger = get_task_logger(__name__)


class ManagementUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'General Information'
    IS_OPTIONAL = True
    SHEETS = [SheetName.management]

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'well_name': None,
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

    def convert_record(self, sheet_name, data, raw_record: list):
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
        try:
            return well.management
        except Exception:
            return None

    def update_with_init_data(self, well, record):
        """Convert record."""
        init_data = WellData(
            well,
            feature_types=self.feature_types, purposes=self.purposes,
            status=self.status, units=self.units,
            organisations=self.organisations,
            groundwater_uses=self.groundwater_uses,
            confinements=self.confinements,
            aquifer_types=self.aquifer_types
        )
        for key, value in init_data.management().items():
            if record['management'][key] in ["", None]:
                record['management'][key] = value
        for key, value in init_data.management_license().items():
            if record['management']['license'][key] in ["", None]:
                record['management']['license'][key] = value
        return record
