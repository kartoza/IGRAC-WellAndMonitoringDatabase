# -*- coding: utf-8 -*-
"""Generate country geometry"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Refresh materialized views'
    views = [
        'mv_well', 'mv_well_measurement',
        'istsos.measures_group', 'istsos.observed_properties_sensor'
    ]

    def handle(self, *args, **options):
        with connections[settings.GWML2_DATABASE_CONFIG].cursor() as cursor:
            for view in self.views:
                sql = f'REFRESH MATERIALIZED VIEW {view}'
                cursor.execute(sql)
