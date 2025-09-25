from gwml2.management.commands.base import WellCommand
from gwml2.models.well import Well


class Command(WellCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        wells = self.wells(**options)
        ids = list(wells.order_by('id').values_list('id', flat=True))
        count = wells.count()
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            cache = well.cache
            cache.assign_data_cache_information()
            print(f'----- {idx}/{count} -----')
