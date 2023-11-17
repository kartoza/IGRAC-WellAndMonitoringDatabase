from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.download_request import DownloadRequest

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def prepare_download_file(self, id: int):
    """Prepare download file of request."""
    try:
        download_request = DownloadRequest.objects.get(id=id)
        download_request.generate_file()
    except DownloadRequest.DoesNotExist:
        pass
