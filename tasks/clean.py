import os

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache

from gwml2.models.download_request import DownloadRequest

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 5
LOCK_ID = 'clean_download_file_lock'


@shared_task(
    bind=True,
    name='gwml2.tasks.clean.clean_download_file',
    queue='geoserver.events')
def clean_download_file(self):
    """Run clean download file."""

    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    if not acquire_lock():
        logger.info('CLEAN_DOWNLOAD_FILE: Task is already running. Skipping.')
        return

    try:
        logger.info('CLEAN_DOWNLOAD_FILE: Running.')
        for download in DownloadRequest.objects.all():
            if download.age_hours >= 10:
                _file = download.file()
                if _file:
                    os.remove(_file)
    finally:
        cache.delete(LOCK_ID)
