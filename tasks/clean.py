import os

from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.download_request import DownloadRequest

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name='gwml2.tasks.clean.clean_download_file',
    queue='geoserver.events')
def clean_download_file(self):
    """Run clean download file."""
    for download in DownloadRequest.objects.all():
        if download.age_hours >= 10:
            _file = download.file()
            if _file:
                os.remove(_file)
