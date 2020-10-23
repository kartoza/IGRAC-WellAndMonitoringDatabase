import uuid
import os
import shutil
import zipfile

from django.conf import settings
from django.http import JsonResponse
from shutil import copyfile
from openpyxl import load_workbook

from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.models.well import Well
from gwml2.tasks.controller import update_progress

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def download_well(self, filters=None):
    DJANGO_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))

    logger.debug('----- begin download  -------')
    if filters:
        # TODO :
        #  implement filters
        wells = Well.objects.filter()
    else:
        wells = Well.objects.all()
    total_records = wells.count()
    logger.debug('Found {} wells'.format(total_records))

    # save it to media
    unique_id = uuid.uuid4()
    folder = os.path.join(
        settings.MEDIA_ROOT, 'gwml2', 'download', str(unique_id)
    )
    if not os.path.exists(folder):
        os.makedirs(folder)

    # create file
    wells_filename = 'wells.xlsx'
    wells_file = os.path.join(folder, wells_filename)
    monitoring_filename = 'monitoring_data.xlsx'
    monitoring_file = os.path.join(folder, monitoring_filename)

    # copy template to actual folder
    copyfile(
        os.path.join(
            DJANGO_ROOT, 'gwml2', 'fixtures', 'download_template', wells_filename),
        wells_file)
    copyfile(
        os.path.join(
            DJANGO_ROOT, 'gwml2', 'fixtures', 'download_template', monitoring_filename),
        monitoring_file)

    # open sheet
    well_book = load_workbook(wells_file)
    well_sheet = well_book.active

    monitor_book = load_workbook(monitoring_file)
    level_measurement_sheet = monitor_book['Level Measurement']
    quality_measurement_sheet = monitor_book['Quality Measurement']
    yield_measurement_sheet = monitor_book['Yield Measurement']

    for index, well in enumerate(wells):
        process_percent = (index / total_records) * 100
        update_progress(process_percent)

        # append data
        well_sheet.append([
            well.original_id,
            well.name,
            well.feature_type.__str__() if well.feature_type else '',
            well.purpose.__str__() if well.purpose else '',
            well.location.y,
            well.location.x,
            well.ground_surface_elevation.value if well.ground_surface_elevation else '',
            well.ground_surface_elevation.unit.name if well.ground_surface_elevation else '',
            well.top_borehole_elevation.value if well.top_borehole_elevation else '',
            well.top_borehole_elevation.unit.name if well.top_borehole_elevation and well.top_borehole_elevation.unit else '',
            well.country.__str__() if well.country else '',
            well.address,
            well.description,
        ])

        # level
        for measurement in well.welllevelmeasurement_set.all():
            level_measurement_sheet.append([
                well.original_id,
                well.country.__str__() if well.country else '',
                measurement.time.strftime('%Y-%m-%d %H:%M:%S'),
                measurement.parameter.__str__() if measurement.parameter else '',
                measurement.value.value if measurement.value else '',
                measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                measurement.methodology
            ])

        # quality
        for measurement in well.wellqualitymeasurement_set.all():
            quality_measurement_sheet.append([
                well.original_id,
                well.country.__str__() if well.country else '',
                measurement.time.strftime('%Y-%m-%d %H:%M:%S'),
                measurement.parameter.__str__() if measurement.parameter else '',
                measurement.value.value if measurement.value else '',
                measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                measurement.methodology
            ])
        # yield
        for measurement in well.wellyieldmeasurement_set.all():
            yield_measurement_sheet.append([
                well.original_id,
                well.country.__str__() if well.country else '',
                measurement.time.strftime('%Y-%m-%d %H:%M:%S'),
                measurement.parameter.__str__() if measurement.parameter else '',
                measurement.value.value if measurement.value else '',
                measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                measurement.methodology
            ])

    well_book.save(wells_file)
    monitor_book.save(monitoring_file)

    # zipping files
    zip_filename = '{}.zip'.format(str(unique_id))
    zip_file = os.path.join(
        settings.MEDIA_ROOT, 'gwml2', 'download', zip_filename
    )
    zip_file = zipfile.ZipFile(zip_file, 'w')
    zip_file.write(wells_file, wells_filename, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.write(monitoring_file, monitoring_filename, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    shutil.rmtree(folder)

    url = os.path.join(settings.MEDIA_URL, 'gwml2', 'download', zip_filename)
    update_progress(100, {
        'url': url
    })
    return JsonResponse({'status': 'success'})
