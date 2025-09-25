from gwml2.management.commands.base import WellCommand
from gwml2.models.general import Country


class Command(WellCommand):
    """ Run download cache."""

    Model = Country

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        countries = self.query(**options)
        count = countries.count()
        for idx, country in enumerate(countries.order_by('code')):
            print(f'----- {idx}/{count} -----')
            country.assign_data_cache_information()
