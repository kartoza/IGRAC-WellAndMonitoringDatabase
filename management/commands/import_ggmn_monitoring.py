__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '08/02/21'

import os
from django.core.management.base import BaseCommand
from gwml2.management.commands.ggmn_importer import (
    NSGGMNData, StandardGGMNData
)


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Reupdate all fixtures.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file_name',
            dest='file_name',
            default='',
            help='specific filename')

    def handle(self, *args, **options):
        file_name = options.get('file_name')
        DJANGO_ROOT = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        fixture_folder = os.path.join(
            DJANGO_ROOT, 'fixtures')

        # let's import
        NSGGMNData(fixture_folder, file_name)
        StandardGGMNData(fixture_folder, file_name)
