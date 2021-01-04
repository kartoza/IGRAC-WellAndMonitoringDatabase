from celery.utils.log import get_task_logger

from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.models.general import Unit
from gwml2.tasks.uploader.base import BaseUploader

logger = get_task_logger(__name__)


class MonitoringDataUploader(BaseUploader):
    """ Save well uploader from excel """
    AUTOCREATE_WELL = False
    SHEETS = [
        'Groundwater Level',
        'Groundwater Quality',
        'Abstraction-Discharge'
    ]

    # key related with the index of keys
    # value if it has tem
    RECORD_FORMAT = {
        'original_id': None,
        'time': None,
        'parameter': TermMeasurementParameter,
        'value_value': None,
        'value_unit': Unit,
        'methodology': None
    }

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        if sheet_name == self.SHEETS[0]:
            key = 'level_measurement'
        elif sheet_name == self.SHEETS[1]:
            key = 'quality_measurement'
        else:
            key = 'yield_measurement'
        data['id'] = None
        return {
            key: [data]
        }

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        if sheet_name == self.SHEETS[0]:
            MODEL = WellLevelMeasurement
            key = 'level_measurement'
        elif sheet_name == self.SHEETS[1]:
            MODEL = WellQualityMeasurement
            key = 'quality_measurement'
        else:
            MODEL = WellYieldMeasurement
            key = 'yield_measurement'

        try:
            return MODEL.objects.get(
                well=well,
                time=record[key][0]['time'],
                parameter=record[key][0]['parameter']
            )
        except MODEL.DoesNotExist:
            return None
