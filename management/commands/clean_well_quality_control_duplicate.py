from django.core.management.base import BaseCommand
from django.db.models import Count

from gwml2.models.well import Well
from gwml2.models.well_quality_control import WellQualityControl


class Command(BaseCommand):
    """Remove wells that have duplicate WellQualityControl records and
    recreate a fresh one for each of them."""

    def handle(self, *args, **options):
        orphan_well_ids = list(
            WellQualityControl.objects.exclude(
                well_id__in=Well.objects.values_list('id', flat=True)
            ).values_list('well_id', flat=True)
        )
        orphan_count = len(orphan_well_ids)
        print(f'----- FOUND {orphan_count} orphan quality controls -----')
        for idx, well_id in enumerate(orphan_well_ids):
            print(f'----- {idx + 1}/{orphan_count} - well {well_id} -----')
            WellQualityControl.objects.filter(well_id=well_id).delete()

        duplicate_well_ids = list(
            WellQualityControl.objects.values('well_id')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
            .values_list('well_id', flat=True)
        )
        count = len(duplicate_well_ids)
        print(f'----- FOUND {count} duplicate wells -----')
        for idx, well_id in enumerate(duplicate_well_ids):
            print(f'----- {idx + 1}/{count} - well {well_id} -----')
            WellQualityControl.objects.filter(well_id=well_id).delete()
            quality_control = WellQualityControl.objects.create(
                well_id=well_id
            )
            quality_control.run()