from celery import shared_task
from celery.utils.log import get_task_logger

from gwml2.models.well import Well

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def generate_measurement_cache(self, well_id: int, model: str = None):
    try:
        print(f'Generate measurement for {well_id}')
        logger.debug(f'Generate measurement for {well_id}')
        well = Well.objects.get(id=well_id)
        well.generate_measurement_cache(model)
    except Well.DoesNotExist:
        print(f'Well {well_id} does not exists')
        logger.debug(f'Well {well_id} does not exists')
