from django.core.management.base import BaseCommand

from gwml2.models.well import Well


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update number of measurement of all well.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-ids',
            '--ids',
            dest='ids',
            default='',
            help='List id of wells'
        )
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
        parser.add_argument(
            '-from_id',
            '--from_id',
            dest='from_id',
            help='From id'
        )
        parser.add_argument(
            '-country_code',
            '--country_code',
            dest='country_code',
            help='From country code'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        # Filter by from_id
        wells = Well.objects.all()

        ids = options.get('ids', None)
        if ids:
            wells = Well.objects.filter(id__in=ids.split(','))

        from_id = options.get('from_id', False)
        if from_id:
            wells = Well.objects.filter(id__gte=from_id)

        # Check country code
        country_code = options.get('country_code', False)
        if country_code:
            wells = wells.filter(country__code=country_code)

        # Run the script
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        ids.sort()
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f"{idx + 1}/{count} : Generating {well.id}")

            well.generate_all_measurement_caches(
                options.get('measurement_name', None),
                force
            )
