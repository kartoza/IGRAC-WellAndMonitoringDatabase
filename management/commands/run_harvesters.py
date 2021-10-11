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
        parser.add_argument(
            '-replace',
            '--replace',
            dest='replace',
            default=False,
            help='Replace the measurement data')
        parser.add_argument(
            '-original_id',
            '--original_id',
            dest='original_id',
            default=None,
            help='Filter just original id')

    def handle(self, *args, **options):
        id = options.get('id', None)
        replace = options.get('replace', False)
        original_id = options.get('original_id', None)
        replace = True if replace in ['True', 'true', 'y'] else replace
        if id:
            queryset = Harvester.objects.filter(id=int(id))
        else:
            queryset = Harvester.objects.all()
        for harvester in queryset:
            harvester.run(replace, original_id)
