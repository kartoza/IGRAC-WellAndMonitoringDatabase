from django.core.management.base import BaseCommand
from django.db.models import Count

from gwml2.models.well_quality_control import WellQualityControl


class Command(BaseCommand):
    """Remove wells that have duplicate WellQualityControl records and
    recreate a fresh one for each of them."""

    def handle(self, *args, **options):
        duplicate_well_ids = list(
            WellQualityControl.objects.values('well_id')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
            .values_list('well_id', flat=True)
        )
        count = len(duplicate_well_ids)
        for idx, well_id in enumerate(duplicate_well_ids):
            print(f'----- {idx + 1}/{count} - well {well_id} -----')
            WellQualityControl.objects.filter(well_id=well_id).delete()
            quality_control = WellQualityControl.objects.create(
                well_id=well_id
            )
            quality_control.run()