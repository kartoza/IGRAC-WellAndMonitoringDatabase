from django.contrib.gis.geos import Point
from django.http import JsonResponse
from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.models.general import Quantity, Unit
from gwml2.models.well import Well
from gwml2.tasks.controller import update_progress

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def well_from_excel(self, location_records, level_records):
    logger.debug('----- begin processing excel -------')
    logger.debug('Found {} locations'.format(len(location_records)))
    # logger.debug('Found {} levels'.format(len(level_records)))

    location_records_length = len(location_records)
    level_records_length = 0
    total_records = location_records_length + level_records_length
    item = 0
    if location_records:
        for record in location_records:
            item += 1

            # update the percentage of progress
            process_percent = (item / total_records) * 100
            update_progress(process_percent)

            # skip if it is title
            if record[0].lower() == 'id well':
                continue
            point = Point(x=record[3], y=record[2], srid=4326)

            well, created = Well.objects.get_or_create(
                original_id=record[0],
                defaults={
                    'location': point
                }
            )
            if not well.elevation:
                well.elevation = Quantity.objects.create(
                    value=record[1],
                    unit=Unit.objects.get(name='m')
                )
            well.location = point
            well.save()

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
    update_progress(100)
    return JsonResponse({'status': 'success'})
