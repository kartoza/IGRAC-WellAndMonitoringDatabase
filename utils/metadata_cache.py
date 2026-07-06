import datetime

from django.db.models import Count, Min, Max, Q


class MetadataCache:
    """MetadataCache class."""

    def __init__(
            self,
            data_date_start, data_date_end, count_measurement,
            count_measurement_level, count_measurement_level_midnight,
            count_measurement_quality, count_measurement_quality_midnight,
            count_measurement_yield, count_measurement_yield_midnight
    ):
        """Init MetadataCache."""
        self.data_date_start = data_date_start
        self.data_date_end = data_date_end
        self.count_measurement = count_measurement
        self.count_measurement_level = count_measurement_level
        self.count_measurement_level_midnight = count_measurement_level_midnight
        self.count_measurement_quality = count_measurement_quality
        self.count_measurement_quality_midnight = count_measurement_quality_midnight
        self.count_measurement_yield = count_measurement_yield
        self.count_measurement_yield_midnight = count_measurement_yield_midnight


def generate_metadata_cache(well_ids, generate_midnight=False):
    """Compute measurement and well stats plus date range for the
    given well ids.

    If generate_midnight is True, also count measurements taken exactly
    at midnight per type. This is off by default since it is an extra
    filtered count on top of the total.

    Returns a tuple of (well_ids, json) where json contains
    data_date_start, data_date_end and data_stats.
    """
    from gwml2.models.well import (
        Well, WellLevelMeasurement, WellQualityMeasurement,
        WellYieldMeasurement
    )

    midnight = datetime.time(0, 0, 0)
    stats = {}

    # 3 queries: one per model, each returns total (+ midnight count if
    # requested) and date range (min/max time) in one aggregate
    measurement_steps = [
        (
            WellLevelMeasurement,
            'count_measurement_level',
            'count_measurement_level_midnight'
        ),
        (
            WellQualityMeasurement,
            'count_measurement_quality',
            'count_measurement_quality_midnight'
        ),
        (
            WellYieldMeasurement,
            'count_measurement_yield',
            'count_measurement_yield_midnight'
        ),
    ]
    start_dates = []
    end_dates = []
    for Model, total_key, midnight_key in measurement_steps:
        aggregates = {
            'total': Count('id'),
            'min_date': Min('time'),
            'max_date': Max('time'),
        }
        if generate_midnight:
            aggregates['midnight'] = Count(
                'id', filter=Q(time__time=midnight)
            )
        result = Model.objects.filter(
            well_id__in=well_ids
        ).aggregate(**aggregates)
        stats[total_key] = result['total']
        if generate_midnight:
            stats[midnight_key] = result['midnight']
        if result['min_date']:
            start_dates.append(result['min_date'])
            end_dates.append(result['max_date'])

    stats['count_measurement'] = (
            stats.get('count_measurement_level', 0)
            + stats.get('count_measurement_quality', 0)
            + stats.get('count_measurement_yield', 0)
    )

    # 1 query: all well counts in one aggregate
    well_stats = Well.objects.filter(id__in=well_ids).aggregate(
        count_well=Count('id'),
        count_well_with_level=Count(
            'id',
            filter=Q(number_of_measurements_level__gt=0)
        ),
        count_well_with_quality=Count(
            'id',
            filter=Q(number_of_measurements_quality__gt=0)
        ),
        count_spring=Count(
            'id',
            filter=Q(feature_type__name__iexact='Spring')
        ),
    )
    stats.update(well_stats)

    json = {
        'data_date_start': min(start_dates) if start_dates else None,
        'data_date_end': max(end_dates) if end_dates else None,
        'data_stats': stats,
    }
    return well_ids, json
