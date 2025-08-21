from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well


class Command(WellCommand):
    """Generate measurement cache."""
    args = ''
    help = 'Generate measurement cache.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-measurement_name',
            '--measurement_name',
            dest='measurement_name',
            default='',
            help='Name of measurement'
        )
        parser.add_argument(
            '-force',
            '--force',
            default='',
            dest='force',
            help='Force to regenerate',
            action='store_true'
        )

    def handle(self, *args, **options):
        """Handle command."""
        # Run the script
        well_ids = self.well_ids(**options)
        count = len(well_ids)
        for idx, id in enumerate(well_ids):
            well = Well.objects.get(id=id)
            print(f"{idx + 1}/{count} : Generating {well.id}")

            well.cache.generate_measurement_cache(
                measurement_name=options.get('measurement_name', None),
                force=options.get('force', False)
            )
