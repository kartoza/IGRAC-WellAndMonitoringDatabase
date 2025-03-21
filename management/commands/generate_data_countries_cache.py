from gwml2.management.commands.base import WellCommand
from gwml2.models.general import Country
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class Command(WellCommand):
    """ Run download cache"""

    Model = Country

    def add_arguments(self, parser):
        """Add command arguments"""
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        countries = self.query(**options)
        for country in countries.order_by('code'):
            generate_data_country_cache(country_code=country.code)
