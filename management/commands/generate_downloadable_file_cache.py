from django.core.management.base import BaseCommand

from gwml2.tasks.downloadable_well_cache import (
    generate_downloadable_file_cache
)


class Command(BaseCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-country',
            '--country',
            dest='country',
            help='Country name or code')
        parser.add_argument(
            '-is_from',
            '--is_from',
            dest='is_from',
            help='Is from country')

    def handle(self, *args, **options):
        country = options.get('country', None)
        is_from = options.get('is_from', False)
        generate_downloadable_file_cache(country=country, is_from=is_from)
