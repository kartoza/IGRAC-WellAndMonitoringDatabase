# -*- coding: utf-8 -*-
"""Generate country geometry"""

import os

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.contrib.gis.geos import Polygon
from django.core.management.base import BaseCommand

from gwml2.models.general_information import Country


class Command(BaseCommand):
    help = 'Generate country geometry'

    def handle(self, *args, **options):
        shp_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            'country_boundaries.shp'
        )
        data_source = DataSource(shp_path)
        layer = data_source[0]
        for feature in layer:
            country_code = feature['country'].value
            try:
                country = Country.objects.get(code=country_code)
                geometry = GEOSGeometry(feature.geom.wkt, srid=4326)
                if isinstance(geometry, Polygon):
                    geometry = MultiPolygon(geometry, srid=4326)
                country.geometry = geometry
                country.save()
            except Country.DoesNotExist:
                pass
