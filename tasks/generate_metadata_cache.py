from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

from gwml2.tasks.file_lock import file_lock

logger = get_task_logger(__name__)

LOCK_ID = 'generate_organisation_country_quality_control_cache.lock'


@shared_task(
    bind=True,
    name='gwml2.tasks.generate_organisation_country_quality_control_cache',
    queue='update',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def generate_organisation_country_quality_control_cache(self):
    """Regenerate organisation and country metadata cache.

    Runs the existing management commands for each so the dashboard
    statistics (organisation/country metadata cache) stay up to date
    for all records.
    """
    with file_lock(LOCK_ID) as lock:
        if lock is None:
            return

        logger.info('Generating organisation metadata cache')
        call_command('generate_organisations_metadata_cache')

        logger.info('Generating country metadata cache')
        call_command('generate_countries_metadata_cache')