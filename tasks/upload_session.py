from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.upload_session import UploadSession

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def run_harvester(self, harvester_id: int):
    try:
        harvester = Harvester.objects.get(id=harvester_id)
        harvester.run()
    except Harvester.DoesNotExist:
        logger.debug('Harvester {} does not exists'.format(harvester_id))


@shared_task(
    bind=True,
    name='gwml2.tasks.upload_session.resume_all_uploader',
    queue='geoserver.events'
)
def resume_all_uploader(self):
    """Resume all uploader."""
    print('RESUME_ALL_UPLOADER')
    for session in UploadSession.running_sessions():
        print(f'Resume {session.id}')
        session.resume()
