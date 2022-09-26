from django.core.management.base import BaseCommand

from gwml2.harvesters.admin import HARVESTERS
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.term import TermFeatureType
from gwml2.models.well_management.organisation import Organisation


class Command(BaseCommand):
    """ Create harversters
    """

    def handle(self, *args, **options):
        try:
            feature_type = TermFeatureType.objects.get(name='Water well')
            for harvester_class in HARVESTERS:
                if harvester_class[2]:
                    harvester, created = Harvester.objects.get_or_create(
                        harvester_class=harvester_class[0],
                        defaults={
                            'name': harvester_class[1],
                            'feature_type': feature_type,
                            'save_missing_well': True
                        }
                    )
                    if created:
                        org, created = Organisation.objects.get_or_create(
                            name=harvester_class[2]
                        )
                        harvester.organisation = org
                        harvester.save()
        except TermFeatureType.DoesNotExist:
            print('Water well feature type does not exist.')
