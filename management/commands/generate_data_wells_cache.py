from django.core.management.base import BaseCommand

from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.data_file_cache.wells_cache import generate_data_well_cache


class Command(BaseCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
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
        parser.add_argument(
            '-force',
            '--force',
            action='store_true',
            dest='force',
            help='Force to recreate the data'
        )

    def handle(self, *args, **options):
        from_id = options.get('from_id', False)
        country_code = options.get('country_code', False)
        force = options.get('force', False)

        # Filter by from_id
        if from_id:
            wells = Well.objects.filter(id__gte=from_id)
        else:
            wells = Well.objects.all()

        # Check country code
        if country_code:
            wells = wells.filter(country__code=country_code)

        # Regenerate cache
        countries = []
        count = wells.count()
        for idx, well in enumerate(wells.order_by('id')):
            print(f'----- {idx}/{count} -----')
            generate_data_well_cache(
                well.id, force_regenerate=force, generate_country_cache=False
            )

            # Save the country code
            if well.country and well.country.code not in countries:
                countries.append(well.country.code)

        # Regenerate country cache
        countries.sort()
        for country in countries:
            generate_data_country_cache(country_code=country)
