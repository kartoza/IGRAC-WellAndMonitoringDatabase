import datetime
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from celery import shared_task
from celery.utils.log import get_task_logger
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from gwml2.models.general import Quantity, Unit, Country
from gwml2.models.well import Well, WellLevelMeasurement
from gwml2.models.term import TermWellPurpose, TermWellStatus, TermFeatureType, TermReferenceElevationType
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import UploadSession

logger = get_task_logger(__name__)

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

MONITORING_ID = 0
MONITORING_DATE_AND_TIME = 1
MONITORING_PARAMETER = 2
MONITORING_VALUE = 3
MONITORING_UNIT = 4
MONITORING_METHOD = 5


def validate_monitoring_records(organisation, records):
    """ Validate monitoring records

       :param organisation: Organisation of the uploader
       :type organisation: Organisation

       :param records: list of monitoring records from excel
       :type records: list

       :return: whether the records are validated, error/success message
       :rtype: bool, str
    """
    # Check if ids are all unique
    row = 2
    for record in records:
        row += 1
        record_id = '{org}-{id}'.format(
            org=organisation.name,
            id=record[ID]
        )
        if not Well.objects.filter(original_id=record_id).exists():
            return (
                False, 'One of the IDs does not exist : '
                       '{id}, row {row}'.format(
                    id=record[ID],
                    row=row
                )
            )
    return True, 'OK'


def validate_well_records(organisation, records):
    """ Validate well records

       :param organisation: Organisation of the uploader
       :type organisation: Organisation

       :param records: list of Well records from excel
       :type records: list

       :return: whether the records are validated, error/success message
       :rtype: bool, str
    """
    # Check if ids are all unique
    row = 2
    for record in records:
        row += 1
        record_id = '{org}-{id}'.format(
            org=organisation.name,
            id=record[ID]
        )
        if Well.objects.filter(original_id=record_id).exists():
            return (
                False, 'One of the IDs is not unique : {id}, row {row}'.format(
                    id=record[ID],
                    row=row
                )
            )
    return True, 'OK'


@shared_task(bind=True, queue='update')
def test_celery(self):
    logger.debug('Upload session does not exists')


def getRecordByIndex(record, INDEX):
    """ Return record by index """
    try:
        return record[INDEX]
    except IndexError:
        return None


def _processing_well_descriptor_file(upload_session):
    logger.debug('----- Begin processing excel -------')

    well_location_file = upload_session.upload_file
    organisation = upload_session.organisation

    location_records = []
    if well_location_file:
        well_location_file.seek(0)
        sheet = None
        if str(well_location_file).split('.')[-1] == 'xls':
            sheet = xls_get(well_location_file, column_limit=20)
        elif str(well_location_file).split('.')[-1] == 'xlsx':
            sheet = xlsx_get(well_location_file, column_limit=20)
        if sheet:
            sheet_name = next(iter(sheet))
            location_records = sheet[sheet_name]
    location_records = location_records[2:]

    logger.debug('Found {} wells'.format(len(location_records)))

    location_records_length = len(location_records)
    level_records_length = 0
    total_records = location_records_length + level_records_length
    item = 0

    if location_records:
        validated, message = validate_well_records(
            organisation, location_records)
        if not validated:
            upload_session.update_progress(
                finished=True,
                status=message,
                progress=0
            )
            return message

        for record in location_records:
            item += 1

            _id = getRecordByIndex(record, ID)
            _lon = getRecordByIndex(record, LON)
            _lat = getRecordByIndex(record, LAT)
            _country = getRecordByIndex(record, COUNTRY)
            _status = getRecordByIndex(record, STATUS)
            _purpose = getRecordByIndex(record, PURPOSE)
            _feature_type = getRecordByIndex(record, FEATURE_TYPE)
            _ground_elevation_unit = getRecordByIndex(record, GROUND_ELEVATION_UNIT)
            _ground_elevation_number = getRecordByIndex(record, GROUND_ELEVATION_NUMBER)
            _top_casing_elevation_unit = getRecordByIndex(record, TOP_CASING_ELEVATION_UNIT)
            _top_casing_elevation_number = getRecordByIndex(record, TOP_CASING_ELEVATION_NUMBER)
            _description = getRecordByIndex(record, DESCRIPTION)
            _address = getRecordByIndex(record, ADDRESS)

            record_id = '{org}-{id}'.format(
                org=organisation.name,
                id=_id
            )

            # update the percentage of progress
            process_percent = (item / total_records) * 100
            upload_session.update_progress(
                status='Processing well : {}'.format(record_id),
                progress=int(process_percent)
            )

            point = Point(x=_lon, y=_lat, srid=4326)

            additional_fields = {}

            if _country:
                additional_fields['country'], _ = (
                    Country.objects.get_or_create(
                        code=_country
                    )
                )

            if _status:
                additional_fields['status'], _ = (
                    TermWellStatus.objects.get_or_create(
                        name=_status
                    )
                )
            if _purpose:
                additional_fields['purpose'], _ = (
                    TermWellPurpose.objects.get_or_create(
                        name=_purpose
                    )
                )

            if _feature_type:
                additional_fields['feature_type'], _ = (
                    TermFeatureType.objects.get_or_create(
                        name=_feature_type
                    )
                )

            if (
                    _ground_elevation_unit and
                    _ground_elevation_number
            ):
                elevation_unit, _ = (
                    Unit.objects.get_or_create(
                        name=_ground_elevation_unit)
                )
                ground_surface_elevation = Quantity.objects.create(
                    value=_ground_elevation_number,
                    unit=elevation_unit
                )
                additional_fields['ground_surface_elevation'] = (
                    ground_surface_elevation
                )

            if (
                    _top_casing_elevation_unit and
                    _top_casing_elevation_number
            ):
                top_casing_elevation_unit, _ = (
                    Unit.objects.get_or_create(
                        name=_top_casing_elevation_unit)
                )
                top_casing_elevation_quantity = Quantity.objects.create(
                    value=_top_casing_elevation_number,
                    unit=top_casing_elevation_unit
                )
                additional_fields['top_borehole_elevation'] = (
                    top_casing_elevation_quantity
                )

            try:
                additional_fields['description'] = _description
            except IndexError:
                pass

            Well.objects.get_or_create(
                original_id=record_id,
                location=point,
                address=_address,
                **additional_fields
            )

    upload_session.update_progress(
        finished=True,
        progress=100,
        status='Added {} well data'.format(len(location_records))
    )


def _processing_well_monitoring_file(upload_session):
    well_monitoring_file = upload_session.upload_file
    organisation = upload_session.organisation

    records = []
    if well_monitoring_file:
        well_monitoring_file.seek(0)
        sheet = None
        if str(well_monitoring_file).split('.')[-1] == 'xls':
            sheet = xls_get(well_monitoring_file, column_limit=15)
        elif str(well_monitoring_file).split('.')[-1] == 'xlsx':
            sheet = xlsx_get(well_monitoring_file, column_limit=15)
        if sheet:
            sheet_name = next(iter(sheet))
            records = sheet[sheet_name]
    records = records[2:]

    logger.debug('Found {} monitoring'.format(len(records)))

    location_records_length = len(records)
    level_records_length = 0
    total_records = location_records_length + level_records_length
    item = 0
    added = 0
    updated = 0

    if records:
        validated, message = validate_monitoring_records(
            organisation, records)
        if not validated:
            upload_session.update_progress(
                finished=True,
                status=message,
                progress=0
            )
            return message

        for record in records:
            item += 1

            _id = getRecordByIndex(record, ID)
            _monitoring_date_and_time = getRecordByIndex(record, MONITORING_DATE_AND_TIME)
            _monitoring_parameter = getRecordByIndex(record, MONITORING_PARAMETER)
            _monitoring_value = getRecordByIndex(record, MONITORING_VALUE)
            _monitoring_unit = getRecordByIndex(record, MONITORING_UNIT)
            _monitoring_method = getRecordByIndex(record, MONITORING_METHOD)

            record_id = '{org}-{id}'.format(
                org=organisation.name,
                id=_id
            )

            # update the percentage of progress
            process_percent = (item / total_records) * 100
            upload_session.update_progress(
                status='Processing monitoring : {}'.format(record_id),
                progress=int(process_percent)
            )

            additional_fields = {}

            # -- Well
            well = Well.objects.get(original_id=record_id)

            # -- Date and time ('%Y-%m-%d %H:%M:%S') e.g '2020-10-20 14:00:00'
            date_and_time = datetime.datetime.strptime(
                str(_monitoring_date_and_time).split('.')[0],
                '%Y-%m-%d %H:%M:%S'
            )

            # -- Parameter
            parameter = _monitoring_parameter
            measurement_parameter, _ = (
                TermMeasurementParameter.objects.get_or_create(
                    name=parameter
                )
            )

            # -- Value & Unit
            value = _monitoring_value
            unit = _monitoring_unit
            if value and unit:
                measurement_unit, _ = (
                    Unit.objects.get_or_create(
                        name=unit
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

            level, created = WellLevelMeasurement.objects.get_or_create(
                well=well,
                time=date_and_time,
                parameter=measurement_parameter,
                **additional_fields
            )

            if created:
                added += 1
            else:
                updated += 1

    else:
        upload_session.update_progress(
            finished=True,
            progress=0,
            status='No monitoring data found'
        )
        return

    upload_session.update_progress(
        finished=True,
        progress=100,
        status=(
            'Added {added} monitoring data'.format(
                added=added)
        )
    )


@shared_task(bind=True, queue='update')
def well_from_excel(self, upload_session_token):
    try:
        upload_session = UploadSession.objects.get(token=upload_session_token)
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')
        return

    if upload_session.category == 'well_upload':
        _processing_well_descriptor_file(upload_session)
    elif upload_session.category == 'well_monitoring_upload':
        _processing_well_monitoring_file(upload_session)

    return JsonResponse({'status': 'success'})
