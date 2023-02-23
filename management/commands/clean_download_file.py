from django.core.management.base import BaseCommand

from gwml2.tasks.clean import clean_download_file


class Command(BaseCommand):
    """ Clean download file request if expired (1 day)"""

    def handle(self, *args, **options):
        clean_download_file()
