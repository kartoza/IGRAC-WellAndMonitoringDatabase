from django.core.management.base import BaseCommand

from gwml2.models.well_management.organisation import Organisation
from gwml2.tasks.data_file_cache.organisation_cache import (
    generate_data_organisation_cache
)


class Command(BaseCommand):
    """ Run download cache by organisation
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

    def handle(self, *args, **options):
        id = options.get('id', False)
        from_id = options.get('from_id', False)

        if id:
            organisations = Organisation.objects.filter(
                id=id,
                active=True
            )
        elif from_id:
            organisations = Organisation.objects.filter(
                id__gte=from_id,
                active=True
            )
        else:
            organisations = Organisation.objects.filter(
                active=True
            )
        # Regenerate organisation cache
        count = organisations.count()
        for idx, organisation in enumerate(organisations.order_by('id')):
            print(f'----- {idx}/{count} -----')
            generate_data_organisation_cache(organisation_id=organisation.id)
