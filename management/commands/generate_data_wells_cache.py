from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.data_file_cache.organisation_cache import (
    generate_data_organisation_cache
)


class Command(WellCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
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
        wells = self.wells(**options)
        generators = options.get('generators', None)
        # Regenerate cache
        countries = []
        organisations = []
        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            print(f'----- {idx}/{count} - {well.id} -----')
            well.cache.generate_data_wells_cache(
                force=options.get('force', False),
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
