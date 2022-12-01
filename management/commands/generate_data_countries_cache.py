from django.core.management.base import BaseCommand

from gwml2.models.general import Country
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class Command(BaseCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-country_code',
            '--country_code',
            dest='country_code',
            help='From country code'
        )

    def handle(self, *args, **options):
        country_code = options.get('country_code', False)

        # Regenerate country cache
        countries = Country.objects.all()
        if country_code:
            countries = countries.filter(code=country_code)
        for country in countries.order_by('code'):
            generate_data_country_cache(country_code=country.code)
