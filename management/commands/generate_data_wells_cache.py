from django.core.management.base import BaseCommand

from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.data_file_cache.organisation_cache import (
    generate_data_organisation_cache
)
from gwml2.tasks.data_file_cache.wells_cache import generate_data_well_cache


class Command(BaseCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id'
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
        parser.add_argument(
            '-force',
            '--force',
            action='store_true',
            dest='force',
            help='Force to recreate the data'
        )
        parser.add_argument(
            '-generators',
            '--generators',
            dest='generators',
            help="Filter by generators : ['general_information','hydrogeology','management','drilling_and_construction','monitor'] in comma separator"
        )

    def handle(self, *args, **options):
        id = options.get('id', False)
        from_id = options.get('from_id', False)
        country_code = options.get('country_code', False)
        force = options.get('force', False)

        # Filter by from_id
        if id:
            wells = Well.objects.filter(id=id)
        elif from_id:
            wells = Well.objects.filter(id__gte=from_id)
        else:
            wells = Well.objects.all()

        # Check country code
        if country_code:
            wells = wells.filter(country__code=country_code)

        generators = options.get('generators', None)

        # Regenerate cache
        countries = []
        organisations = []
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f'----- {idx}/{count} - {well.id} -----')
            generate_data_well_cache(
                well.id, force_regenerate=force,
                generate_country_cache=False,
                generate_organisation_cache=False,
                generators=generators.split(',') if generators else None
            )

            # Save the country code
            if well.country and well.country.code not in countries:
                countries.append(well.country.code)
            if well.organisation and well.organisation.id not in organisations:
                organisations.append(well.organisation.id)

        # Regenerate country cache
        countries.sort()
        for country in countries:
            generate_data_country_cache(country_code=country)

        # Regenerate organisation cache
        organisations.sort()
        for organisation_id in organisations:
            generate_data_organisation_cache(organisation_id=organisation_id)
