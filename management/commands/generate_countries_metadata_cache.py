from gwml2.management.commands.base import WellCommand
from gwml2.models.general import Country


class Command(WellCommand):
    """Run countries generate_metadata_cache"""

    Model = Country

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        countries = self.query(**options)

        # Regenerate countries cache
        count = countries.count()
        for idx, country in enumerate(countries.order_by('id')):
            print(f'----- {idx + 1}/{count} -----')
            print(
                'Generate metadata cache for country '
                f'{country.name} - Start'
            )
            country.assign_metadata_cache()
            print(
                'Generate metadata cache for country '
                f'{country.name} - Done'
            )
