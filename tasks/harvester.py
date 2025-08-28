from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from gwml2.harvesters.models.harvester import Harvester, HarvesterLog, DONE
from gwml2.tasks.file_lock import file_lock

logger = get_task_logger(__name__)

LOCK_ID = 'run_all_harvester.lock'


@shared_task(bind=True, queue='update')
def run_harvester(self, harvester_id: int):
    from gwml2.models.site_preference import SitePreference
    try:
        SitePreference.update_running_harvesters()
        pref = SitePreference.load()
        running_ids = pref.running_harvesters.values_list(
            'id', flat=True
        ).order_by('id')

        if harvester_id in running_ids:
            return

        harvester = Harvester.objects.get(id=harvester_id)
        if self.request.id:
            harvester.task_id = self.request.id
            harvester.save(update_fields=["task_id"])
            harvester.run()
    except Harvester.DoesNotExist:
        logger.debug('Harvester {} does not exists'.format(harvester_id))


@shared_task(
    bind=True,
    name='gwml2.tasks.harvester.run_all_harvester',
    queue='update',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def run_all_harvester(self):
    """Run All harvesters."""
    # 1. Get current running harvesters
    from gwml2.models.site_preference import SitePreference
    with file_lock(LOCK_ID) as lock:
        if lock is None:
            return

        pref = SitePreference.load()

        # Get the current latest running id
        running_ids = pref.running_harvesters.values_list(
            'id', flat=True
        ).order_by('id')
        latest_id = running_ids.last()
        if not latest_id:
            latest_id = 0

        # Get upcoming ids
        # Greater than equal to the latest running id
        # And from first
        one_day_ago = timezone.now() - timedelta(days=1)
        recent_harvesters = HarvesterLog.objects.filter(
            end_time__gte=one_day_ago,
            status=DONE
        ).values_list('harvester_id', flat=True)
        harvesters = Harvester.objects.filter(active=True).exclude(
            id__in=running_ids
        ).exclude(id__in=recent_harvesters)
        upcoming_ids = list(
            harvesters.filter(id__gt=latest_id).order_by('id').values_list(
                'id', flat=True)
        ) + list(
            harvesters.order_by('id').values_list('id', flat=True)
        )

        SitePreference.update_running_harvesters()
        pref.refresh_from_db()
        running_count = pref.running_harvesters.order_by('id').count()

        # Get the different between max and running count
        number_of_new_harvester = (
                pref.running_harvesters_concurrency_count - running_count
        )

        # Run every id for the next queue in the remaining slot
        for idx in range(number_of_new_harvester):
            try:
                _id = upcoming_ids[idx]
                run_harvester.delay(_id)
            except (Harvester.DoesNotExist, IndexError):
                pass

        SitePreference.update_running_harvesters()
        pref.refresh_from_db()
