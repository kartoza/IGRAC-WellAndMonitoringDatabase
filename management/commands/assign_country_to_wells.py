from django.core.management.base import BaseCommand

from gwml2.models import Well


class Command(BaseCommand):
    """ Assign country of wells"""
    args = ''
    help = 'Assign country of wells.'

    def handle(self, *args, **options):
        query = Well.objects.filter(country__isnull=True)
        total = query.count()
        for idx, well in enumerate(query):
            print(f'{idx}/{total}')
            well.assign_country()
