from django.core.management.base import BaseCommand

from gwml2.models.well import Well


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update measurement type of well.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-ids',
            '--ids',
            dest='ids',
            default='',
            help='List id of wells'
        )
        parser.add_argument(
            '-force',
            '--force',
            dest='force',
            help='Force to regenerate',
            action='store_true'
        )

    def handle(self, *args, **options):
        # Filter by from_id
        wells = Well.objects.all()
        ids = options.get('ids', None)
        if ids:
            wells = Well.objects.filter(id__in=ids.split(','))
        # Check if force
        force = options.get('force', False)
        if not force:
            wells = wells.filter(
                measurement_cache_generated_at__isnull=True
            )

        for well in wells:
            well.measurement_cache_generated_at_check()
