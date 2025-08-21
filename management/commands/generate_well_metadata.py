from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well


class Command(WellCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-force',
            '--force',
            action='store_true',
            dest='force',
            help='Force to recreate the data'
        )

    def handle(self, *args, **options):
        wells = self.wells(**options)
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f'----- {idx}/{count} - {well.id} -----')
            well.cache.generate_metadata(
                force=options.get('force', False)
            )
