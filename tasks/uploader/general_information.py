from celery.utils.log import get_task_logger

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus
)
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.terms import SheetName
from gwml2.utils.well_data import WellData

logger = get_task_logger(__name__)


class GeneralInformationUploader(BaseUploader):
    """ Save well uploader from excel """
    UPLOADER_NAME = 'General Information'
    AUTOCREATE_WELL = True
    IS_OPTIONAL = False
    SHEETS = [SheetName.general_information]

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
        'address': None,
        'license_type': None,
        'license_restriction': None,
        'is_groundwater_level': None,
        'is_groundwater_quality': None,
        'first_measurement': None,
        'last_measurement': None
    }

    def convert_record(self, sheet_name, data, raw_record: list):
        """ return object that will be used
        """
        key = 'is_groundwater_level'
        if data.get(key, None) is not None:
            data[key] = data[key].lower()
        key = 'is_groundwater_quality'
        if data.get(key, None) is not None:
            data[key] = data[key].lower()

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
        for key, value in init_data.general_information().items():
            if record['general_information'][key] in ["", None]:
                record['general_information'][key] = value
        for key, value in init_data.license().items():
            if record['well_metadata'][key] in ["", None]:
                record['well_metadata'][key] = value
        return record
