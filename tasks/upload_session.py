from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.upload_session import UploadSession

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name='gwml2.tasks.upload_session.resume_all_uploader',
    queue='update'
)
def resume_all_uploader(self):
    """Resume all uploader."""
    print('RESUME_ALL_UPLOADER')
    for session in UploadSession.running_sessions():
        print(f'Resume {session.id}')
        session.resume()
