import os
import time

from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.download_request import DownloadRequest
from gwml2.tasks.file_lock import file_lock

logger = get_task_logger(__name__)

_5_HOURS_IN_SECONDS = 5 * 60 * 60


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

        output_folder = DownloadRequest.output_folder
        if not os.path.exists(output_folder):
            return

        now = time.time()
        for fname in os.listdir(output_folder):
            fpath = os.path.join(output_folder, fname)
            if not os.path.isfile(fpath) or not fname.endswith('.zip'):
                continue
            age_seconds = now - os.path.getmtime(fpath)
            if age_seconds >= _5_HOURS_IN_SECONDS:
                try:
                    os.remove(fpath)
                    logger.info(f"Deleted file: {fpath}")
                except Exception as e:
                    logger.warning(f"Failed to delete {fpath}: {e}")
