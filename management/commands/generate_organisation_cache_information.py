from gwml2.management.commands.base import WellCommand
from gwml2.models.well_management.organisation import Organisation


class Command(WellCommand):
    """ Run download cache
    """

    Model = Organisation

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        organisations = self.query(**options)
        organisations = organisations.filter(active=True)

        # Regenerate organisation cache
        count = organisations.count()
        for idx, organisation in enumerate(organisations.order_by('id')):
            print(f'----- {idx}/{count} -----')
            organisation.assign_data_cache_information()
