from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from gwml2.models.site_preference import SitePreference
from gwml2.models.upload_session import UploadSession
from gwml2.tasks.file_lock import file_lock

LOCK_EXPIRE = 60 * 10
LOCK_ID = 'resume_all_uploader.lock'

logger = get_task_logger(__name__)


def uploads_to_be_resumed():
    """Return uploads to be resumed."""
    from_date = timezone.now() - timedelta(days=30)
    return UploadSession.running_sessions().filter(retry__lte=5).filter(
        uploaded_at__gte=from_date
    )


@shared_task(
    bind=True,
    name='gwml2.tasks.upload_session.resume_all_uploader',
    queue='update',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def resume_all_uploader(self):
    """Resume all uploader."""
    with file_lock(LOCK_ID) as lock:
        if lock is None:
            return

        preference = SitePreference.load()
        print(
            f'{LOCK_ID} settings : {preference.batch_upload_auto_resume}'
        )
        if not preference.batch_upload_auto_resume:
            print(f'{LOCK_ID} : SKIPPED')
            return

        query = uploads_to_be_resumed()
        print(f'{LOCK_ID} : {query.count()}')
        for session in query:
            print(f'{LOCK_ID} Resume {session.id}')
            session.resume()
