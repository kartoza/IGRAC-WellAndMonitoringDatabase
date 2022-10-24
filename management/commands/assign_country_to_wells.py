from django.core.management.base import BaseCommand

from gwml2.models import Well


class Command(BaseCommand):
    """ Assign country of wells"""
    args = ''
    help = 'Assign country of wells.'

    def handle(self, *args, **options):
        total = Well.objects.count()
        for idx, well in enumerate(Well.objects.all()):
            print(f'{idx}/{total}')
            well.assign_country()
