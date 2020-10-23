from django.contrib.gis.geos import Point
from django.http import JsonResponse
from celery import shared_task
from celery.utils.log import get_task_logger
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from gwml2.models.general import Quantity, Unit, Country
from gwml2.models.well import Well
from gwml2.models.term import TermWellPurpose, TermFeatureType, TermReferenceElevationType
from gwml2.models.upload_session import UploadSession
from gwml2.models.reference_elevation import ReferenceElevation

logger = get_task_logger(__name__)

ID = 0
NAME = 1
FEATURE_TYPE = 2
PURPOSE = 3
LAT = 4
LON = 5
GROUND_ELEVATION_NUMBER = 6
GROUND_ELEVATION_UNIT = 7
TOP_CASING_ELEVATION_NUMBER = 8
TOP_CASING_ELEVATION_UNIT = 9
COUNTRY = 10
ADDRESS = 11
DESCRIPTION = 12


def validate_well_records(organisation, records):
    """ Validate well records

       :param organisation: Organisation of the uploader
       :type organisation: Organisation

       :param records: list of Well records from excel
       :type records: list

       :return: are records validated, error/success message
       :rtype: bool, str
    """
    # Check if ids are all unique
    for record in records:
        record_id = '{org}-{id}'.format(
            org=organisation.name,
            id=record[ID]
        )
        if Well.objects.filter(original_id=record_id).exists():
            return False, 'One of the ID is not unique : {}'.format(
                record[ID]
            )
    return True, 'OK'


@shared_task(bind=True, queue='update')
def test_celery(self):
    logger.debug('Upload session does not exists')


@shared_task(bind=True, queue='update')
def well_from_excel(self, upload_session_token):

    try:
        upload_session = UploadSession.objects.get(token=upload_session_token)
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')
        return

    logger.debug('----- Begin processing excel -------')

    well_location_file = upload_session.upload_file
    organisation = upload_session.organisation

    location_records = []
    if well_location_file:
        well_location_file.seek(0)
        sheet = None
        if str(well_location_file).split('.')[-1] == 'xls':
            sheet = xls_get(well_location_file, column_limit=15)
        elif str(well_location_file).split('.')[-1] == 'xlsx':
            sheet = xlsx_get(well_location_file, column_limit=15)
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
            record_id = '{org}-{id}'.format(
                org=organisation.name,
                id=record[ID]
            )

            # update the percentage of progress
            process_percent = (item / total_records) * 100
            upload_session.update_progress(
                status='Processing {}'.format(record_id),
                progress=int(process_percent)
            )

            point = Point(x=record[LON], y=record[LAT], srid=4326)

            additional_fields = {}

            if record[COUNTRY]:
                additional_fields['country'], _ = (
                    Country.objects.get_or_create(
                        code=record[COUNTRY]
                    )
                )

            if record[PURPOSE]:
                additional_fields['purpose'], _ = (
                    TermWellPurpose.objects.get_or_create(
                        name=record[PURPOSE]
                    )
                )

            if record[FEATURE_TYPE]:
                additional_fields['feature_type'], _ = (
                    TermFeatureType.objects.get_or_create(
                        name=record[FEATURE_TYPE]
                    )
                )

            if (
                record[GROUND_ELEVATION_UNIT] and
                record[GROUND_ELEVATION_NUMBER]
            ):
                elevation_unit, _ = (
                    Unit.objects.get_or_create(
                        name=record[GROUND_ELEVATION_UNIT])
                )
                ground_surface_elevation = Quantity.objects.create(
                    value=record[GROUND_ELEVATION_NUMBER],
                    unit=elevation_unit
                )
                additional_fields['ground_surface_elevation'] = (
                    ground_surface_elevation
                )

            if (
                record[TOP_CASING_ELEVATION_UNIT] and
                record[TOP_CASING_ELEVATION_NUMBER]
            ):
                top_casing_elevation_unit, _ = (
                    Unit.objects.get_or_create(
                        name=record[TOP_CASING_ELEVATION_UNIT])
                )
                top_casing_elevation_quantity = Quantity.objects.create(
                    value=record[TOP_CASING_ELEVATION_NUMBER],
                    unit=top_casing_elevation_unit
                )
                additional_fields['top_borehole_elevation'] = (
                    top_casing_elevation_quantity
                )

            try:
                additional_fields['description'] = record[DESCRIPTION]
            except IndexError:
                pass

            Well.objects.get_or_create(
                original_id=record_id,
                location=point,
                address=record[ADDRESS],
                **additional_fields
            )

    # TODO:
    #  Not sure which model for level records
    # if level_records:
    #     for record in level_records:
    #         item += 1
    #
    #         # update the percentage of progress
    #         process_percent = (item / total_records) * 100
    #         update_progress(process_percent)
    #
    #         # skip if it is title
    #         if record[0].lower == 'time':
    #             continue
    #
    #         try:
    #             well = GWWell.objects.get(gw_well_name=record[3])
    #             time = dateparse.parse_datetime(record[0])
    #             depth = Quantity.objects.create(
    #                 value=record[2],
    #                 unit='meter'
    #             )
    #             well_level_log = GWGeologyLog.objects.create(
    #                 phenomenon_time=time,
    #                 result_time=time,
    #                 gw_level=record[2],
    #                 reference=record[1],
    #                 gw_well=well,
    #                 start_depth=depth,
    #                 end_depth=depth
    #             )
    #         except GWWell.DoesNotExist:
    #             pass
    upload_session.update_progress(
        finished=True,
        progress=100,
        status='All {} records has been added'.format(len(location_records))
    )
    return JsonResponse({'status': 'success'})
