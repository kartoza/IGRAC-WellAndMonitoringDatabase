import itertools
from datetime import timedelta

from celery import shared_task

from gwml2.tasks.file_lock import file_lock

LOCK_ID = 'generate_well_level_not_daily_cache.lock'

# Anything gap smaller than this between two consecutive level
# measurements means the well has finer-than-daily data.
DAILY_GAP_THRESHOLD = timedelta(hours=23)

BATCH_SIZE = 500


def _pairwise(iterable):
    """Yield consecutive (previous, current) pairs, lazily."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


@shared_task(
    bind=True,
    name='gwml2.tasks.generate_well_level_not_daily_cache',
    queue='update',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def generate_well_level_not_daily_cache(self, ids=None):
    """Generate the Well.is_level_not_daily cache flag.

    A well is flagged True when at least two consecutive level
    measurements are less than DAILY_GAP_THRESHOLD apart.
    """
    from gwml2.models.well import Well

    with file_lock(LOCK_ID) as lock:
        if lock is None:
            return

        wells = Well.objects.all()
        if ids:
            wells = wells.filter(id__in=ids)
        well_ids = list(wells.order_by('id').values_list('id', flat=True))
        count = len(well_ids)

        batch = []
        for idx, well_id in enumerate(well_ids):
            well = Well.objects.get(id=well_id)
            print(f'----- {idx + 1}/{count} - {well.id} -----')

            times = (
                well.welllevelmeasurement_set
                .order_by('time')
                .values_list('time', flat=True)
                .iterator()
            )
            is_not_daily = any(
                b - a < DAILY_GAP_THRESHOLD
                for a, b in _pairwise(times)
                if a and b
            )

            if well.is_level_not_daily != is_not_daily:
                well.is_level_not_daily = is_not_daily
                batch.append(well)

            if len(batch) >= BATCH_SIZE:
                Well.objects.bulk_update(batch, ['is_level_not_daily'])
                batch = []

        if batch:
            Well.objects.bulk_update(batch, ['is_level_not_daily'])