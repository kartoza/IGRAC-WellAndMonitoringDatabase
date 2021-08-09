from django.core.management.base import BaseCommand
from gwml2.harvesters.models.harvester import Harvester


class Command(BaseCommand):
    """ Run all harvester
    """

    def handle(self, *args, **options):
        for harvester in Harvester.objects.all():
            harvester.run()
