# -*- coding: utf-8 -*-
"""Generate country geometry"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Refresh materialized views'

    def handle(self, *args, **options):
        with connections[settings.GWML2_DATABASE_CONFIG].cursor() as cursor:
            cursor.execute('REFRESH MATERIALIZED VIEW mv_well_ggmn')
            cursor.execute('REFRESH MATERIALIZED VIEW mv_well')
