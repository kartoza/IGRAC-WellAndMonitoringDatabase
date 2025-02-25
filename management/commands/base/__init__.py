from django.core.management.base import BaseCommand

from gwml2.models.well import Well


class WellCommand(BaseCommand):
    """Base for well command."""
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

    def wells(self, **options):
        """Get all wells"""

        # Filter by from_id
        wells = Well.objects.all()

        ids = options.get('ids', None)
        if ids:
            wells = Well.objects.filter(
                id__in=ids.replace(' ', '').split(',')
            )

        from_id = options.get('from_id', False)
        if from_id:
            wells = Well.objects.filter(id__gte=from_id)

        # Check country code
        country_code = options.get('country_code', False)
        if country_code:
            wells = wells.filter(
                country__code__in=country_code.split(',')
            )

        return wells

    def well_ids(self, **options):
        """Get well ids."""
        ids = list(
            self.wells(**options).order_by('id').values_list('id', flat=True)
        )
        ids.sort()
        return ids
