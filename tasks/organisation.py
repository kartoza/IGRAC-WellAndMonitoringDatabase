from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def update_ggis_uid(self, id):
    from gwml2.models import Organisation
    Organisation.objects.get(pk=id).update_ggis_uid()


@shared_task(bind=True, queue='update')
def generate_metadata_cache(self, ids):
    from gwml2.models import Organisation
    for organisation in Organisation.objects.filter(pk__in=ids):
        print(
            'Generate metadata cache for organisation '
            f'{organisation.name} - Start'
        )
        organisation.assign_metadata_cache(generate_midnight=True)
        print(
            'Generate metadata cache for organisation '
            f'{organisation.name} - Done'
        )
