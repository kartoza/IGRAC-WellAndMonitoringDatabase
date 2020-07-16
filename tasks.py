import math
from django.utils import dateparse
from django.contrib.gis.geos import Point
from django.http import JsonResponse
from celery import task, current_task
from gwml2.models.well import GWWell, GWGeologyLog
from gwml2.models.universal import Quantity


@task(
    bind=True,
    name="gwml2.process_excel",)
def process_excel(self, location_records, level_records):
    print('----- begin processing excel -------')
    print(len(location_records))
    print(len(level_records))

    location_records_length = len(location_records)
    level_records_length = len(level_records)
    total_records = location_records_length + level_records_length
    process_percent = 0
    item = 0
    if location_records:
        for record in location_records:
            item += 1
            if record[0].lower() == 'id well':
                continue

            point = Point(x=record[3], y=record[2], srid=4326)
            try:
                well = GWWell.objects.get(gw_well_name=record[0])
                well.gw_well_location = point
                well.gw_well_total_length = record[1]
                well.save()
            except GWWell.DoesNotExist:
                well = GWWell.objects.create(
                    gw_well_name=record[0],
                    gw_well_location=point,
                    gw_well_total_length=record[1]
                )
            process_percent = math.ceil(item / total_records) * 100
            current_task.update_state(
                state='PROGRESS',
                meta={'process_percent': process_percent})

    if level_records:
        for record in level_records:
            item += 1
            if record[0].lower == 'time':
                continue

            try:
                well = GWWell.objects.get(gw_well_name=record[3])
                time = dateparse.parse_datetime(record[0])
                depth = Quantity.objects.create(
                    value=record[2],
                    unit='meter'
                )
                well_level_log = GWGeologyLog.objects.create(
                    phenomenon_time=time,
                    result_time=time,
                    gw_level=record[2],
                    reference=record[1],
                    gw_well=well,
                    start_depth=depth,
                    end_depth=depth
                )
            except GWWell.DoesNotExist:
                pass
            process_percent = math.ceil(item / total_records) * 100
            current_task.update_state(
                state='PROGRESS',
                meta={'process_percent': process_percent})
    current_task.update_state(
        state='PROGRESS',
        meta={'process_percent': process_percent})
    print('------ finish processing excel -------')

    return JsonResponse({'status': 'success'})
