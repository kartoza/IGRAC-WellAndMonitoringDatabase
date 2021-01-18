from django.core.management.base import BaseCommand
from gwml2.models.well import Well


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update number of measurement of all well.'

    def handle(self, *args, **options):
        count = Well.objects.count()
        for idx, well in enumerate(Well.objects.all()):
            print('{}/{}'.format(idx + 1, count))
            well.number_of_measurements = well.welllevelmeasurement_set.count() + \
                                          well.wellqualitymeasurement_set.count() + \
                                          well.wellyieldmeasurement_set.count()
            well.save()
