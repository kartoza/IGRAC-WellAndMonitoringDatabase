from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well


class Command(WellCommand):
    """ Run measurement group data generation
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-force',
            '--force',
            dest='force',
            action='store_true',
            help='Force regenerate the measurement group data'
        )

    def handle(self, *args, **options):
        wells = self.wells(**options)
        ids = list(wells.order_by('id').values_list('id', flat=True))
        count = wells.count()
        force = options.get('force', False)
        for idx, id in enumerate(ids):
            print(f'----- {idx + 1}/{count} : Measurement group start -----')
            well = Well.objects.get(id=id)
            cache = well.cache
            cache.generate_measurement_group_data(force=force)
            print(f'----- {idx + 1}/{count} : Measurement group finish -----')
