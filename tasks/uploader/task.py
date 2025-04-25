from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.upload_session import UploadSession

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def well_batch_upload(self, upload_session_id: str, restart: bool = False):
    try:
        upload_session = UploadSession.objects.get(id=upload_session_id)
        upload_session.task_id = self.request.id
        upload_session.is_canceled = False
        upload_session.save()
        upload_session.run(restart)
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')


@shared_task(bind=True, queue='update')
def well_batch_upload_create_report(self, upload_session_id: str, restart: bool = False):
    try:
        upload_session = UploadSession.objects.get(id=upload_session_id)
        upload_session.create_report_excel()
        upload_session.save()
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')
