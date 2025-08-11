from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well


class Command(WellCommand):
    """Run quality control check of well."""

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        wells = self.wells(**options)
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f'----- {idx}/{count} - {well.id} -----')
            well.quality_control.run()
