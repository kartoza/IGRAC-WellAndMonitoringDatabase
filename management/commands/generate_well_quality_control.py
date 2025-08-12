from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well
from gwml2.models.well_quality_control import WellQualityControl

class Command(WellCommand):
    """Run quality control check of well."""

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-force',
            '--force',
            default='',
            dest='force',
            help='Force to regenerate',
            action='store_true'
        )

    def handle(self, *args, **options):
        wells = self.wells(**options)
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f'----- {idx}/{count} - {well.id} -----')
            if options.get('force', False):
                WellQualityControl.objects.all().update(
                    groundwater_level_time_gap_generated_time=None,
                    groundwater_level_value_gap_generated_time=None,
                    groundwater_level_strange_value_generated_time=None

                )
            # If it is old,
            well.quality_control.run()
