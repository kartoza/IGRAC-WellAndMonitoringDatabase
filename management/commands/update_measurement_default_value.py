from django.core.management.base import BaseCommand
from django.db.models.signals import post_save, pre_save

from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import WellYieldMeasurement, WellQualityMeasurement, \
    WellLevelMeasurement, Well
from gwml2.signals.well import (
    post_save_measurement_for_cache,
    pre_save_measurement, post_save_measurement
)
from gwml2.utilities import Signal, temp_disconnect_signals


def update_measurement_default_db(id, query, init):
    total = query.count()
    for idx, measurement in enumerate(query):
        output = measurement.set_default_value(init)
        if not output:
            print(f'{id} - {idx}/{total}')
            measurement.save()


def assign_first_last(query, well: Well):
    first = query.order_by('time').first()
    if first and (
            not well.first_time_measurement or
            first.time <= well.first_time_measurement
    ):
        well.first_time_measurement = first.time

    last = query.order_by('time').last()
    if last and (
            not well.last_time_measurement or
            last.time >= well.first_time_measurement
    ):
        well.last_time_measurement = last.time
    return well


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
        parser.add_argument(
            '-init',
            '--init',
            action='store_true',
            dest='init',
            help='Init data'
        )

    def handle(self, *args, **options):
        id = options.get('id', False)
        from_id = options.get('from_id', False)
        init = options.get('init', False)

        # Filter by from_id
        if id:
            wells = Well.objects.filter(id=id)
        elif from_id:
            wells = Well.objects.filter(id__gte=from_id)
        else:
            wells = Well.objects.all()

        for param in TermMeasurementParameter.objects.all():
            param.default_unit = param.units.first()
            param.save()

        for well in wells.filter(first_time_measurement__isnull=True).order_by('number_of_measurements', 'id'):
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
                    well.id, well.welllevelmeasurement_set.all(), init
                )
                update_measurement_default_db(
                    well.id, well.wellyieldmeasurement_set.all(), init
                )
                update_measurement_default_db(
                    well.id, well.wellqualitymeasurement_set.all(), init
                )
                
                assign_first_last(well.welllevelmeasurement_set.all(), well)
                assign_first_last(well.wellyieldmeasurement_set.all(), well)
                assign_first_last(well.wellqualitymeasurement_set.all(), well)
                well.save()
