import os

from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.download_request import DownloadRequest
from gwml2.tasks.file_lock import file_lock

logger = get_task_logger(__name__)


@shared_task(
    bind=True, name='gwml2.tasks.clean.clean_download_file',
    queue='geoserver.events',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def clean_download_file(self):
    """Run clean download file using reusable file lock."""
    filename = 'clean_download_file.lock'
    with file_lock(filename) as lock:
        if lock is None:
            return

        for download in DownloadRequest.objects.all():
            if download.age_hours >= 10:
                _file = download.file()
                if _file:
                    try:
                        os.remove(_file)
                        logger.info(f"Deleted file: {_file}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {_file}: {e}")
