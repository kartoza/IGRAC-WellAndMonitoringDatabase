import datetime
from django.contrib.gis.geos import Point
from django.db import transaction
from django.http import JsonResponse
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


class BatchUploader(object):
    """ Uploader for well """
    START_ROW = 2

    def __init__(self, upload_session: UploadSession):
        self.upload_session = upload_session

    def get_column(self, record: dict, INDEX: int):
        """ Return column with index
        """
        try:
            return record[INDEX]
        except IndexError:
            return None

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
                    record_id = self.get_column(record, ID)

                    self.upload_session.update_progress(
                        progress=int(process_percent),
                        status='Processing well : {}'.format(record_id)
                    )

                    _lon = self.get_column(record, LON)
                    _lat = self.get_column(record, LAT)
                    _country = self.get_column(record, COUNTRY)
                    _status = self.get_column(record, STATUS)
                    _purpose = self.get_column(record, PURPOSE)
                    _feature_type = self.get_column(record, FEATURE_TYPE)
                    _ground_elevation_unit = self.get_column(
                        record, GROUND_ELEVATION_UNIT)
                    _ground_elevation_number = self.get_column(
                        record, GROUND_ELEVATION_NUMBER)
                    _top_casing_elevation_unit = self.get_column(
                        record, TOP_CASING_ELEVATION_UNIT)
                    _top_casing_elevation_number = self.get_column(
                        record, TOP_CASING_ELEVATION_NUMBER)
                    _description = self.get_column(record, DESCRIPTION)
                    _address = self.get_column(record, ADDRESS)

                    point = Point(x=_lon, y=_lat, srid=4326)

                    additional_fields = {
                        'created_by': self.upload_session.uploader,
                        'last_edited_by': self.upload_session.uploader,
                        'address': _address
                    }

                    if _country:
                        additional_fields['country'] = Country.objects.get(
                            code=_country
                        )

                    if _status:
                        additional_fields['status'] = TermWellStatus.objects.get(
                            name=_status
                        )
                    if _purpose:
                        additional_fields['purpose'] = TermWellPurpose.objects.get(
                            name=_purpose
                        )

                    if _feature_type:
                        additional_fields['feature_type'] = TermFeatureType.objects.get(
                            name=_feature_type
                        )

                    if _ground_elevation_unit and _ground_elevation_number:
                        elevation_unit = Unit.objects.get(
                            name=_ground_elevation_unit.lower().strip())
                        ground_surface_elevation = Quantity.objects.create(
                            value=_ground_elevation_number,
                            unit=elevation_unit
                        )
                        additional_fields['ground_surface_elevation'] = (
                            ground_surface_elevation)

                    if _top_casing_elevation_unit and _top_casing_elevation_number:
                        top_casing_elevation_unit = Unit.objects.get(
                            name=_top_casing_elevation_unit.lower().strip())
                        top_casing_elevation_quantity = Quantity.objects.create(
                            value=_top_casing_elevation_number,
                            unit=top_casing_elevation_unit
                        )
                        additional_fields['top_borehole_elevation'] = (
                            top_casing_elevation_quantity)

                    try:
                        additional_fields['description'] = _description
                    except IndexError:
                        pass

                    Well.objects.get_or_create(
                        original_id=record_id,
                        organisation=organisation,
                        location=point,
                        defaults=additional_fields
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
                    _id = self.get_column(record, ID)
                    record_id = 'row {}'.format(index + self.START_ROW)

                    self.upload_session.update_progress(
                        progress=int(process_percent),
                        status='Processing monitoring : {}'.format(record_id)
                    )

                    _monitoring_date_and_time = self.get_column(record, MONITORING_DATE_AND_TIME)
                    _monitoring_parameter = self.get_column(record, MONITORING_PARAMETER)
                    _monitoring_value = self.get_column(record, MONITORING_VALUE)
                    _monitoring_unit = self.get_column(record, MONITORING_UNIT)
                    _monitoring_method = self.get_column(record, MONITORING_METHOD)

                    additional_fields = {}
                    # -- Well
                    well = Well.objects.get(
                        original_id=_id,
                        organisation__name=organisation.name)

                    # -- Date and time ('%Y-%m-%d %H:%M:%S') e.g '2020-10-20 14:00:00'
                    date_and_time = datetime.datetime.strptime(
                        str(_monitoring_date_and_time).split('.')[0],
                        '%Y-%m-%d %H:%M:%S'
                    )
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
                        additional_fields['value'] = Quantity.objects.create(
                            value=value,
                            unit=measurement_unit
                        )

                        # -- Method
                        method = _monitoring_method
                        if method:
                            additional_fields['methodology'] = method

                    level, created = WellLevelMeasurement.objects.update_or_create(
                        well=well,
                        time=date_and_time,
                        parameter=measurement_parameter,
                        defaults=additional_fields
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
