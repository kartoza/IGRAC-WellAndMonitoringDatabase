from gwml2.management.commands.base import WellCommand
from gwml2.models.well import MEASUREMENT_MODELS


class Command(WellCommand):
    """Update measurement cache generated at field."""
    args = ''
    help = 'Update measurement cache generated at field.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-force',
            '--force',
            dest='force',
            help='Force to regenerate',
            action='store_true'
        )

    def handle(self, *args, **options):
        wells = self.wells(**options)
        # Check if force
        force = options.get('force', False)
        if not force:
            wells = wells.filter(
                measurement_cache_generated_at__isnull=True
            )

        count = wells.count()
        for idx, well in enumerate(wells):
            print(f"{idx + 1}/{count} : Generating {well.id}")

            for MeasurementModel in MEASUREMENT_MODELS:
                model = MeasurementModel.__name__
                well.measurement_cache_generated_at_check(model)
