from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def update_ggis_uid(self, id):
    from gwml2.models import Organisation
    Organisation.objects.get(pk=id).update_ggis_uid()


@shared_task(bind=True, queue='update')
def generate_data_stats(self, id, force=False):
    from gwml2.models import Organisation
    Organisation.objects.get(pk=id).generate_data_stats(force=force)
