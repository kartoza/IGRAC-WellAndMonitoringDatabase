from gwml2.management.commands.base import WellCommand
from gwml2.tasks.well_level_not_daily import generate_well_level_not_daily_cache


class Command(WellCommand):
    """Generate Well.is_level_not_daily cache flag."""

    def handle(self, *args, **options):
        ids = list(self.wells(**options).values_list('id', flat=True))
        generate_well_level_not_daily_cache(ids=ids)