import os

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from gwml2.models.download_request import DownloadRequest

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name='gwml2.tasks.harvester.clean_download_file',
    queue='geoserver.events')
def clean_download_file(self):
    """Run clean download file."""
    for download in DownloadRequest.objects.all():
        diff = timezone.now() - download.request_at
        if diff.days >= 1:
            _file = download.file()
            if _file:
                os.remove(_file)
