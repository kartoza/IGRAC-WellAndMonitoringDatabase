# -*- coding: utf-8 -*-
"""Generate country geometry"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections

ALL_VIEWS = [
    'mv_well',
    'mv_well_measurement',
    'istsos.measures_group',
    'istsos.observed_properties_sensor',
]


class Command(BaseCommand):
    help = (
        'Refresh materialized views. '
        'Pass view names as arguments to refresh specific ones, '
        'or omit to refresh all. '
        f'Available: {", ".join(ALL_VIEWS)}'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'views',
            nargs='*',
            choices=[*ALL_VIEWS, []],
            help='Materialized view(s) to refresh. Refreshes all if omitted.',
        )

    def handle(self, *args, **options):
        views = options['views'] or ALL_VIEWS
        invalid = set(views) - set(ALL_VIEWS)
        if invalid:
            self.stderr.write(
                self.style.ERROR(
                    f'Unknown view(s): {", ".join(invalid)}. '
                    f'Available: {", ".join(ALL_VIEWS)}'
                )
            )
            return
        with connections[settings.GWML2_DATABASE_CONFIG].cursor() as cursor:
            for view in views:
                self.stdout.write(f'Refreshing {view}...')
                cursor.execute(f'REFRESH MATERIALIZED VIEW {view}')
                self.stdout.write(self.style.SUCCESS(f'  Done: {view}'))
