import os
import shutil

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from gwml2.models.well import Well

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def clean_dangling_measurement_cache(self):
    """Remove measurement cache that does not have well."""
    folder = os.path.join(settings.MEASUREMENTS_FOLDER)
    logger.info(f'CLEAN_DANGLING_MEASUREMENT_CACHE : {folder} - [START]')

    # List all item inside it
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isfile(full_path):
            try:
                _id = item.split('-')[0]
                Well.objects.get(id=_id)
            except Well.DoesNotExist:
                logger.info(f'Remove {full_path}')
                os.remove(full_path)
        elif os.path.isdir(full_path):
            try:
                Well.objects.get(id=item)
            except Well.DoesNotExist:
                logger.info(f'Remove {full_path}')
                shutil.rmtree(full_path)
    logger.info(f'CLEAN_DANGLING_MEASUREMENT_CACHE : {folder} - [DONE]')


@shared_task(bind=True, queue='update')
def clean_dangling_well_data_cache(self):
    """Remove well data cache that does not have well."""
    folder = os.path.join(os.path.join(settings.GWML2_FOLDER, 'wells-data'))
    logger.info(f'CLEAN_DANGLING_WELL_DATA_CACHE : {folder} - [START]')

    # List all item inside it
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isfile(full_path):
            try:
                _id = item.split('-')[0]
                Well.objects.get(id=_id)
            except Well.DoesNotExist:
                logger.info(f'Remove {full_path}')
                os.remove(full_path)
        elif os.path.isdir(full_path):
            try:
                Well.objects.get(id=item)
            except Well.DoesNotExist:
                logger.info(f'Remove {full_path}')
                shutil.rmtree(full_path)
    logger.info(f'CLEAN_DANGLING_WELL_DATA_CACHE : {folder} - [DONE]')
