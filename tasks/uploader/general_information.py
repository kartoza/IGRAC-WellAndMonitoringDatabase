from celery.utils.log import get_task_logger

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus
)
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class GeneralInformationUploader(BaseUploader):
    """ Save well uploader from excel """
    AUTOCREATE_WELL = True
    SHEETS = [
        'General Information'
    ]
    WELL_AUTOCREATE = True

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'name': None,
        'feature_type': TermFeatureType,
        'purpose': TermWellPurpose,
        'status': TermWellStatus,
        'description': None,
        'latitude': None,
        'longitude': None,
        'ground_surface_elevation_value': None,
        'ground_surface_elevation_unit': Unit,
        'top_borehole_elevation_value': None,
        'top_borehole_elevation_unit': Unit,
        'country': Country,
        'address': None
    }

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        return {
            'general_information': data,
            'well_metadata': {
                'organisation': self.upload_session.organisation.id,
                'public': self.upload_session.public,
                'downloadable': self.upload_session.downloadable
            }
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        return well
