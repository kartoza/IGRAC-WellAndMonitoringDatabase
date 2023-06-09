from django.core.management.base import BaseCommand
from django.db.models.signals import post_save, pre_save

from gwml2.models.well import (
    Well, WellYieldMeasurement, WellQualityMeasurement, WellLevelMeasurement
)
from gwml2.signals.well import (
    post_save_measurement_for_cache,
    pre_save_measurement, post_save_measurement
)
from gwml2.utilities import Signal, temp_disconnect_signals


def update_measurement_default_db(query):
    total = query.count()
    for idx, measurement in enumerate(query):
        print(f'{idx}/{total}')
        measurement.set_default_value()
        measurement.save()


class Command(BaseCommand):
    """ Run download cache
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id'
        )
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
        parser.add_argument(
            '-force',
            '--force',
            action='store_true',
            dest='force',
            help='Force to recreate the data'
        )

    def handle(self, *args, **options):
        id = options.get('id', False)
        from_id = options.get('from_id', False)

        # Filter by from_id
        if id:
            wells = Well.objects.filter(id=id)
        elif from_id:
            wells = Well.objects.filter(id__gte=from_id)
        else:
            wells = Well.objects.all()
        for well in wells:
            with temp_disconnect_signals(
                    [
                        Signal(pre_save, pre_save_measurement,
                               WellLevelMeasurement),
                        Signal(pre_save, pre_save_measurement,
                               WellYieldMeasurement),
                        Signal(pre_save, pre_save_measurement,
                               WellQualityMeasurement),
                        Signal(post_save, post_save_measurement,
                               WellLevelMeasurement),
                        Signal(post_save, post_save_measurement,
                               WellYieldMeasurement),
                        Signal(post_save, post_save_measurement,
                               WellQualityMeasurement),
                        Signal(post_save, post_save_measurement_for_cache,
                               WellLevelMeasurement),
                        Signal(post_save, post_save_measurement_for_cache,
                               WellYieldMeasurement),
                        Signal(post_save, post_save_measurement_for_cache,
                               WellQualityMeasurement),
                    ]
            ):
                update_measurement_default_db(
                    well.welllevelmeasurement_set.all())
                update_measurement_default_db(
                    well.wellyieldmeasurement_set.all())
                update_measurement_default_db(
                    well.wellqualitymeasurement_set.all()
                )
