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
        parser.add_argument(
            '-from_id',
            '--from_id',
            dest='from_id',
            help='From id'
        )
        parser.add_argument(
            '-country_code',
            '--country_code',
            dest='country_code',
            help='From country code'
        )

    def handle(self, *args, **options):
        id = options.get('id', None)
        measurement_name = options.get('measurement_name', None)
        from_id = options.get('from_id', False)
        country_code = options.get('country_code', False)
        force = options.get('force', False)

        # Filter by from_id
        if id:
            wells = Well.objects.filter(id=id)
        elif from_id:
            wells = Well.objects.filter(id__gte=from_id)
        else:
            wells = Well.objects.all()

        # Check country code
        if country_code:
            wells = wells.filter(country__code=country_code)

        count = wells.count()
        ids = list(wells.order_by('id').values_list('id', flat=True))
        for idx, id in enumerate(ids):
            well = Well.objects.get(id=id)
            for MeasurementModel in [
                WellLevelMeasurement, WellQualityMeasurement,
                WellYieldMeasurement
            ]:
                # skip if measurement filtered
                if measurement_name and MeasurementModel.__name__ != measurement_name:
                    continue
                model = MeasurementModel.__name__
                if not force:
                    cache_file = well.return_measurement_cache_path(model)
                    if os.path.exists(cache_file):
                        continue

                print("{}/{} : Generating {}, well {}".format(
                    idx + 1, count, model, well.id)
                )
                well.generate_measurement_cache(model)
