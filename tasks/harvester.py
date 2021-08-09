from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.harvesters.models.harvester import Harvester

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def run_harvester(self, harvester_id: int):
    try:
        harvester = Harvester.objects.get(id=harvester_id)
        harvester.run()
    except Harvester.DoesNotExist:
        logger.debug('Harvester {} does not exists'.format(harvester_id))


@shared_task(bind=True, queue='update')
def run_all_harvester(self):
    for harvester in Harvester.objects.all():
        harvester.run()
