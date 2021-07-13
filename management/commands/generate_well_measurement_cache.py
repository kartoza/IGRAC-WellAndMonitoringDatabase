import os
from django.core.management.base import BaseCommand
from gwml2.models.well import (
    Well, WellLevelMeasurement, WellYieldMeasurement, WellQualityMeasurement)


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update number of measurement of all well.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id',
            dest='id',
            default='',
            help='ID of well')
        parser.add_argument(
            '-measurement_name',
            '--measurement_name',
            dest='measurement_name',
            default='',
            help='Name of measurement')
        parser.add_argument(
            '-force',
            '--force',
            default='',
            dest='force',
            help='Force to regenerate')

    def handle(self, *args, **options):
        id = options.get('id', None)
        measurement_name = options.get('measurement_name', None)
        force = options.get('force', False)
        if id:
            queryset = Well.objects.filter(id=int(id))
        else:
            queryset = Well.objects.all()

        count = queryset.count()
        for idx, well in enumerate(queryset):
            for MeasurementModel in \
                    [WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement]:
                # skip if measurement filtered
                if measurement_name and MeasurementModel.__name__ != measurement_name:
                    continue
                model = MeasurementModel.__name__
                if not force:
                    cache_file = well.return_measurement_cache_path(model)
                    if os.path.exists(cache_file):
                        continue

                print("{}/{} : Generating {}, well {}".format(idx + 1, count, model, well.id))
                well.generate_measurement_cache(model)
