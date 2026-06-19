from django.core.management import call_command

from gwml2.management.commands.base import WellCommand
from gwml2.utils.generate_dem_well_value import assign_glo_90m_elevation


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
        wells = assign_glo_90m_elevation(wells)
        args = []
        kwargs = {
            "ids": ','.join(list(wells.values_list('id', flat=True)))
        }

        call_command(
            "generate_data_wells_cache", *args, **kwargs
        )
