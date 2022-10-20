from django.core.management.base import BaseCommand

from gwml2.harvesters.models.harvester import Harvester


class Command(BaseCommand):
    """ Run all harvester
    """
    true_str = ['true', 'y', 'yes']

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id',
            dest='id',
            default='',
            help='ID of harvester')
        parser.add_argument(
            '-original_id',
            '--original_id',
            dest='original_id',
            default=None,
            help='Filter just original id')
        parser.add_argument(
            '-replace',
            '--replace',
            dest='replace',
            default='f',
            help='Replace the measurement data')

    def handle(self, *args, **options):
        id = options.get('id', None)
        original_id = options.get('original_id', None)

        replace = options.get('replace', 'f')
        replace = True if replace.lower() in self.true_str else False

        if id:
            queryset = Harvester.objects.filter(id=int(id))
        else:
            queryset = Harvester.objects.all()
        for harvester in queryset:
            harvester.run(replace, original_id)
