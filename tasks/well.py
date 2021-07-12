from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.models.well import Well

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def generate_measurement_cache(self, well_id: int, model: str):
    try:
        well = Well.objects.get(id=well_id)
        well.generate_measurement_cache(model)
    except Well.DoesNotExist:
        logger.debug('Well {} does not exists'.format(well_id))
