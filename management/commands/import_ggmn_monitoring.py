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

    def handle(self, *args, **options):
        DJANGO_ROOT = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        fixture_folder = os.path.join(
            DJANGO_ROOT, 'fixtures')

        # let's import
        StandardGGMNData(fixture_folder)
        NSGGMNData(fixture_folder)
