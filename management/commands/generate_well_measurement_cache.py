from django.core.management.base import BaseCommand
from gwml2.models.well import Well


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update number of measurement of all well.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id',
            dest='id',
            default='',
            help='ID of well')
        parser.add_argument(
            '-model',
            '--model',
            dest='model',
            default='',
            help='Model of measurement')

    def handle(self, *args, **options):
        id = options.get('id', None)
        model = options.get('model', None)
        if id:
            queryset = Well.objects.filter(id=int(id))
        else:
            queryset = Well.objects.all()

        count = queryset.count()
        for idx, well in enumerate(queryset):
            print("Generating {}/{}".format(idx + 1, count))
            well.generate_measurement_cache(model)
