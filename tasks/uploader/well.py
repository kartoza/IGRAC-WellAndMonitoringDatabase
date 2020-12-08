import datetime
from django.contrib.gis.geos import Point
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import make_aware
from celery import shared_task
from celery.utils.log import get_task_logger
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from gwml2.models.general import Quantity, Unit, Country
from gwml2.models.well import Well, WellLevelMeasurement
from gwml2.models.term import (
    TermWellPurpose, TermWellStatus, TermFeatureType,
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import (
    UploadSession,
    UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
)

logger = get_task_logger(__name__)

# WELL UPLOAD
ID = 0
NAME = 1
STATUS = 2
FEATURE_TYPE = 3
PURPOSE = 4
LAT = 5
LON = 6
GROUND_ELEVATION_NUMBER = 7
GROUND_ELEVATION_UNIT = 8
TOP_CASING_ELEVATION_NUMBER = 9
TOP_CASING_ELEVATION_UNIT = 10
COUNTRY = 11
ADDRESS = 12
DESCRIPTION = 13

# MONITORING UPLOAD
MONITORING_ID = 0
MONITORING_DATE_AND_TIME = 1
MONITORING_PARAMETER = 2
MONITORING_VALUE = 3
MONITORING_UNIT = 4
MONITORING_METHOD = 5


def create_or_get_well(
        organisation,
        data,
        additional_data = None):
    """Create or get a Well object"""

    original_id = get_column(data, ID)
    _lon = get_column(data, LON)
    _lat = get_column(data, LAT)
    country_code = get_column(data, COUNTRY)
    well_status = get_column(data, STATUS)
    purpose = get_column(data, PURPOSE)
    feature_type = get_column(data, FEATURE_TYPE)
    ground_elevation_unit = get_column(
        data, GROUND_ELEVATION_UNIT)
    ground_elevation_number = get_column(
        data, GROUND_ELEVATION_NUMBER)
    top_casing_elevation_unit = get_column(
        data, TOP_CASING_ELEVATION_UNIT)
    top_casing_elevation_number = get_column(
        data, TOP_CASING_ELEVATION_NUMBER)
    description = get_column(data, DESCRIPTION)
    address = get_column(data, ADDRESS)
    name = get_column(data, NAME)

    location = Point(x=_lon, y=_lat, srid=4326)

    if not additional_data:
        additional_data = {}

    if name:
        additional_data['name'] = name

    if address:
        additional_data['address'] = address

    if description:
        additional_data['description'] = description

    if country_code:
        additional_data['country'] = Country.objects.get(
            code=country_code
        )

    if well_status:
        additional_data['status'] = TermWellStatus.objects.get(
            name=well_status
        )

    if purpose:
        additional_data['purpose'] = TermWellPurpose.objects.get(
            name=purpose
        )

    if feature_type:
        additional_data['feature_type'] = TermFeatureType.objects.get(
            name=feature_type
        )

    if ground_elevation_unit and ground_elevation_number:
        elevation_unit = Unit.objects.get(
            name=ground_elevation_unit.lower().strip())
        ground_surface_elevation = Quantity.objects.create(
            value=ground_elevation_number,
            unit=elevation_unit
        )
        additional_data['ground_surface_elevation'] = (
            ground_surface_elevation)

    if top_casing_elevation_unit and top_casing_elevation_number:
        _top_casing_elevation_unit = Unit.objects.get(
            name=top_casing_elevation_unit.lower().strip())
        _top_casing_elevation_quantity = Quantity.objects.create(
            value=top_casing_elevation_number,
            unit=_top_casing_elevation_unit
        )
        additional_data['top_borehole_elevation'] = (
            _top_casing_elevation_quantity)

    if organisation:
        well, created = Well.objects.get_or_create(
            original_id=original_id,
            organisation=organisation,
            location=location,
        )
    else:
        well, created = Well.objects.get_or_create(
            original_id=original_id,
            location=location,
        )

    Well.objects.filter(id=well.id).update(**additional_data)

    return well, created


def create_monitoring_data(data, organisation_name, additional_data=None):
    """Create a monitoring data from dictionary"""

    if not additional_data:
        additional_data = {}

    well_id = get_column(data, ID)

    _monitoring_date_and_time = get_column(
        data,
        MONITORING_DATE_AND_TIME)
    _monitoring_parameter = get_column(
        data,
        MONITORING_PARAMETER)
    _monitoring_value = get_column(
        data,
        MONITORING_VALUE)
    _monitoring_unit = get_column(
        data,
        MONITORING_UNIT)
    _monitoring_method = get_column(
        data,
        MONITORING_METHOD)

    # -- Well
    if organisation_name:
        well = Well.objects.get(
            original_id=well_id,
            organisation__name=organisation_name)
    else:
        well = Well.objects.get(
            original_id=well_id
        )

    # -- Date and time ('%Y-%m-%d %H:%M:%S') e.g '2020-10-20 14:00:00'
    date_and_time = datetime.datetime.strptime(
        str(_monitoring_date_and_time).split('.')[0],
        '%Y-%m-%d %H:%M:%S'
    )
    aware_date_and_time = make_aware(date_and_time)

    # -- Parameter
    parameter = _monitoring_parameter
    measurement_parameter = (
        TermMeasurementParameter.objects.get(
            name=parameter
        )
    )

    # -- Value & Unit
    value = _monitoring_value
    unit = _monitoring_unit
    if value and unit:
        measurement_unit = (
            Unit.objects.get(
                name=unit.lower().strip()
            )
        )
        additional_data['value'] = Quantity.objects.create(
            value=value,
            unit=measurement_unit
        )

        # -- Method
        method = _monitoring_method
        if method:
            additional_data['methodology'] = method

    if 'last_edited_at' not in additional_data:
        additional_data['last_edited_at'] = make_aware(datetime.datetime.now())
    if 'created_at' not in additional_data:
        additional_data['created_at'] = make_aware(datetime.datetime.now())

    return WellLevelMeasurement.objects.update_or_create(
        well=well,
        time=aware_date_and_time,
        parameter=measurement_parameter,
        defaults=additional_data
    )


def get_column(record: dict, index: int):
    """ Return column data by INDEX
    """
    try:
        return record[index]
    except IndexError:
        return None


class BatchUploader(object):
    """ Uploader for well """
    START_ROW = 2

    def __init__(self, upload_session: UploadSession):
        self.upload_session = upload_session

    def get_records(self):
        """ Get records form upload session """
        _file = self.upload_session.upload_file

        records = []
        if _file:
            _file.seek(0)
            sheet = None
            if str(_file).split('.')[-1] == 'xls':
                sheet = xls_get(_file, column_limit=20)
            elif str(_file).split('.')[-1] == 'xlsx':
                sheet = xlsx_get(_file, column_limit=20)
            if sheet:
                sheet_name = next(iter(sheet))
                records = sheet[sheet_name]
        return records[self.START_ROW:]


class WellUploader(BatchUploader):
    """ Specific for well """

    def process(self):
        """ Process records """
        records = self.get_records()
        organisation = self.upload_session.organisation

        total_records = len(records)
        logger.debug('Found {} wells'.format(total_records))

        process_percent = 0
        record_id = None
        try:
            with transaction.atomic(using='gwml2'):
                for index, record in enumerate(records):
                    process_percent = (index / total_records) * 100
                    record_id = get_column(record, ID)

                    self.upload_session.update_progress(
                        progress=int(process_percent),
                        status='Processing well : {}'.format(record_id)
                    )

                    additional_data = {
                        'created_by': self.upload_session.uploader,
                        'last_edited_by': self.upload_session.uploader
                    }

                    create_or_get_well(
                        organisation=organisation,
                        data=record,
                        additional_data=additional_data
                    )

            self.upload_session.update_progress(
                finished=True,
                progress=100,
                status='Added {} well data'.format(total_records)
            )
        except Country.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Country does not found for {}'.format(record_id)
            )
        except TermWellStatus.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Well status does not found for {}'.format(record_id)
            )
        except TermWellPurpose.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Well purpose does not found for {}'.format(record_id)
            )
        except TermFeatureType.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Feature type does not found for {}'.format(record_id)
            )
        except Unit.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Unit does not found for {}'.format(record_id)
            )
        except Exception as e:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='{}'.format(e)
            )


class WellMonitoringUploader(BatchUploader):
    """ Specific for monitoring upload """

    def process(self):
        """ Process records """
        records = self.get_records()
        organisation = self.upload_session.organisation

        total_records = len(records)
        logger.debug('Found {} monitoring'.format(total_records))

        process_percent = 0
        added = 0
        updated = 0
        record_id = None
        try:
            with transaction.atomic(using='gwml2'):
                for index, record in enumerate(records):
                    process_percent = (index / total_records) * 100
                    record_id = 'row {}'.format(index + self.START_ROW)

                    self.upload_session.update_progress(
                        progress=int(process_percent),
                        status='Processing monitoring : {}'.format(record_id)
                    )

                    level, created = create_monitoring_data(
                        organisation_name=organisation.name,
                        data=record
                    )

                    if created:
                        added += 1
                    else:
                        updated += 1

            self.upload_session.update_progress(
                finished=True,
                progress=100,
                status='Added {} and updated {} monitoring data'.format(added, updated)
            )
        except Well.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Well does not found for {}'.format(record_id)
            )
        except TermMeasurementParameter.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Parameter does not found for {}'.format(record_id)
            )
        except Unit.DoesNotExist:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='Unit does not found for {}'.format(record_id)
            )
        except Exception as e:
            self.upload_session.update_progress(
                finished=True, progress=process_percent,
                status='{}'.format(e)
            )


@shared_task(bind=True, queue='update')
def well_batch_upload(self, upload_session_token: str):
    try:
        upload_session = UploadSession.objects.get(token=upload_session_token)
        if upload_session.category == UPLOAD_SESSION_CATEGORY_WELL_UPLOAD:
            WellUploader(upload_session).process()
        elif upload_session.category == UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD:
            WellMonitoringUploader(upload_session).process()
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')
        return
    return JsonResponse({'status': 'success'})
