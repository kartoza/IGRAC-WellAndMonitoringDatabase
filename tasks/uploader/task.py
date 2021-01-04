from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.tasks.uploader.general_information import GeneralInformationUploader
from gwml2.tasks.uploader.monitoring_data import MonitoringDataUploader

from gwml2.models.upload_session import (
    UploadSession,
    UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
)

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def well_batch_upload(self, upload_session_id: str):
    try:
        upload_session = UploadSession.objects.get(id=upload_session_id)
        if upload_session.category == UPLOAD_SESSION_CATEGORY_WELL_UPLOAD:
            GeneralInformationUploader(upload_session)
        elif upload_session.category == UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD:
            MonitoringDataUploader(upload_session)
    except UploadSession.DoesNotExist:
        logger.debug('Upload session does not exists')
