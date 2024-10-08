from celery.utils.log import get_task_logger

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus
)
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class GeneralInformationUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'General Information'
    AUTOCREATE_WELL = True
    SHEETS = [
        'General Information'
    ]

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
        'glo_90m_elevation_value': None,
        'glo_90m_elevation_unit': Unit,
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
                'license': self.upload_session.license,
                'restriction_code_type': self.upload_session.restriction_code_type,
                'constraints_other': self.upload_session.constraints_other
            },
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        return well
