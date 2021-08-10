from django.core.management.base import BaseCommand
from gwml2.harvesters.models.harvester import Harvester


class Command(BaseCommand):
    """ Run all harvester
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id',
            dest='id',
            default='',
            help='ID of harvester')

    def handle(self, *args, **options):
        id = options.get('id', None)
        if id:
            queryset = Harvester.objects.filter(id=int(id))
        else:
            queryset = Harvester.objects.all()
        for harvester in queryset:
            harvester.run()
