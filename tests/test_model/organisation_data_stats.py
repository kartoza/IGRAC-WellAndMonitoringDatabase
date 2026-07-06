"""Test for Organisation.assign_metadata_cache."""

import datetime

from django.utils import timezone

from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.term import TermFeatureType
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    OrganisationF,
    WellF,
    WellLevelMeasurementF,
    WellQualityMeasurementF,
    WellYieldMeasurementF,
)


class OrganisationAssignMetadataCacheDateRangeTest(GWML2Test):
    """Test for the date range part of Organisation.assign_metadata_cache."""

    def setUp(self):
        """To setup test."""
        self.organisation = OrganisationF(name='Organisation Date Range')

    def test_no_data(self):
        """No harvester and no measurements: nothing is assigned."""
        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        self.assertFalse(self.organisation.data_is_from_api)
        self.assertIsNone(self.organisation.data_date_start)
        self.assertIsNone(self.organisation.data_date_end)

    def test_data_is_from_api_still_computes_date_range(self):
        """Date range is computed from measurements even when a
        Harvester marks the organisation as API-sourced."""
        Harvester.objects.create(
            harvester_class='gwml2.harvesters.harvester.gin_gw_info.GinGWInfo',
            name='Harvester 1',
            organisation=self.organisation
        )
        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1))
        )

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        self.assertTrue(self.organisation.data_is_from_api)
        self.assertEqual(
            self.organisation.data_date_start, datetime.date(2020, 1, 1)
        )
        self.assertEqual(
            self.organisation.data_date_end, datetime.date(2020, 1, 1)
        )

    def test_date_range_from_level_measurements_only(self):
        """Date range is derived from the min/max level measurement
        time."""
        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1))
        )
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2021, 6, 15))
        )

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        self.assertFalse(self.organisation.data_is_from_api)
        self.assertEqual(
            self.organisation.data_date_start, datetime.date(2020, 1, 1)
        )
        self.assertEqual(
            self.organisation.data_date_end, datetime.date(2021, 6, 15)
        )

    def test_date_range_across_all_measurement_types(self):
        """Date range spans the earliest/latest date across level,
        quality and yield measurements."""
        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2019, 3, 1))
        )
        WellQualityMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 5, 1))
        )
        WellYieldMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2022, 8, 20))
        )

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        self.assertEqual(
            self.organisation.data_date_start, datetime.date(2019, 3, 1)
        )
        self.assertEqual(
            self.organisation.data_date_end, datetime.date(2022, 8, 20)
        )

    def test_measurements_of_unrelated_organisation_are_ignored(self):
        """Measurements belonging to wells of another organisation must
        not affect this organisation's date range."""
        other_organisation = OrganisationF(name='Other Organisation')
        other_well = WellF(organisation=other_organisation)
        WellLevelMeasurementF(
            well=other_well,
            time=timezone.make_aware(datetime.datetime(2015, 1, 1))
        )

        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1))
        )

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        self.assertEqual(
            self.organisation.data_date_start, datetime.date(2020, 1, 1)
        )
        self.assertEqual(
            self.organisation.data_date_end, datetime.date(2020, 1, 1)
        )


class OrganisationAssignMetadataCacheStatsTest(GWML2Test):
    """Test for the stats part of Organisation.assign_metadata_cache."""

    def setUp(self):
        """To setup test."""
        self.organisation = OrganisationF(name='Organisation Stats')

    def test_no_wells(self):
        """No wells: every counter is zero and stats/timestamp are
        saved."""
        self.organisation.assign_metadata_cache(generate_midnight=True)
        self.organisation.refresh_from_db()
        stats = self.organisation.data_stats

        self.assertEqual(stats['count_measurement_level'], 0)
        self.assertEqual(stats['count_measurement_level_midnight'], 0)
        self.assertEqual(stats['count_measurement_quality'], 0)
        self.assertEqual(stats['count_measurement_quality_midnight'], 0)
        self.assertEqual(stats['count_measurement_yield'], 0)
        self.assertEqual(stats['count_measurement_yield_midnight'], 0)
        self.assertEqual(stats['count_measurement'], 0)
        self.assertEqual(stats['count_well'], 0)
        self.assertEqual(stats['count_well_with_level'], 0)
        self.assertEqual(stats['count_well_with_quality'], 0)
        self.assertEqual(stats['count_spring'], 0)
        self.assertIsNotNone(self.organisation.metadata_cache_generated_at)

    def test_measurement_counts_including_midnight(self):
        """Measurement counts are totalled per type, with a separate
        count for measurements taken exactly at midnight."""
        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1, 0, 0, 0))
        )
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 2, 8, 30, 0))
        )
        WellQualityMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1, 0, 0, 0))
        )
        WellYieldMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1, 9, 0, 0))
        )

        self.organisation.assign_metadata_cache(generate_midnight=True)
        self.organisation.refresh_from_db()
        stats = self.organisation.data_stats

        self.assertEqual(stats['count_measurement_level'], 2)
        self.assertEqual(stats['count_measurement_level_midnight'], 1)
        self.assertEqual(stats['count_measurement_quality'], 1)
        self.assertEqual(stats['count_measurement_quality_midnight'], 1)
        self.assertEqual(stats['count_measurement_yield'], 1)
        self.assertEqual(stats['count_measurement_yield_midnight'], 0)
        self.assertEqual(stats['count_measurement'], 4)

    def test_well_counts_with_level_quality_and_spring(self):
        """Well counts reflect wells with level/quality data and wells
        that are springs."""
        spring_type = TermFeatureType.objects.create(name='Spring')
        borehole_type = TermFeatureType.objects.create(name='Borehole')

        WellF(
            organisation=self.organisation,
            feature_type=borehole_type,
            number_of_measurements_level=3,
            number_of_measurements_quality=0,
        )
        WellF(
            organisation=self.organisation,
            feature_type=spring_type,
            number_of_measurements_level=0,
            number_of_measurements_quality=2,
        )
        WellF(
            organisation=self.organisation,
            feature_type=borehole_type,
            number_of_measurements_level=0,
            number_of_measurements_quality=0,
        )

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        stats = self.organisation.data_stats

        self.assertEqual(stats['count_well'], 3)
        self.assertEqual(stats['count_well_with_level'], 1)
        self.assertEqual(stats['count_well_with_quality'], 1)
        self.assertEqual(stats['count_spring'], 1)

    def test_recomputes_even_when_stale_stats_are_cached(self):
        """Stats are always recomputed from current data, overwriting
        any stale cached values."""
        well = WellF(organisation=self.organisation)
        WellLevelMeasurementF(
            well=well,
            time=timezone.make_aware(datetime.datetime(2020, 1, 1))
        )

        self.organisation.data_stats = {
            'count_measurement_level': 100,
            'count_measurement_level_midnight': 100,
            'count_measurement_quality': 100,
            'count_measurement_quality_midnight': 100,
            'count_measurement_yield': 100,
            'count_measurement_yield_midnight': 100,
            'count_well': 100,
            'count_well_with_level': 100,
            'count_well_with_quality': 100,
            'count_spring': 100,
        }
        self.organisation.save()

        self.organisation.assign_metadata_cache()
        self.organisation.refresh_from_db()
        stats = self.organisation.data_stats

        self.assertEqual(stats['count_measurement_level'], 1)
        self.assertEqual(stats['count_well'], 1)


class OrganisationMetadataCachePropertyTest(GWML2Test):
    """Test for Organisation.metadata_cache and Organisation.data_types."""

    def setUp(self):
        """To setup test."""
        self.organisation = OrganisationF(name='Organisation Metadata Cache')

    def test_defaults_when_no_stats(self):
        """metadata_cache defaults counts to 0 when data_stats is empty."""
        cache = self.organisation.metadata_cache
        self.assertIsNone(cache.data_date_start)
        self.assertIsNone(cache.data_date_end)
        self.assertEqual(cache.count_measurement, 0)
        self.assertEqual(cache.count_measurement_level, 0)
        self.assertEqual(cache.count_measurement_level_midnight, 0)
        self.assertEqual(cache.count_measurement_quality, 0)
        self.assertEqual(cache.count_measurement_quality_midnight, 0)
        self.assertEqual(cache.count_measurement_yield, 0)
        self.assertEqual(cache.count_measurement_yield_midnight, 0)

    def test_reflects_stored_stats_and_date_range(self):
        """metadata_cache reflects data_stats and date range fields."""
        self.organisation.data_date_start = datetime.date(2020, 1, 1)
        self.organisation.data_date_end = datetime.date(2021, 1, 1)
        self.organisation.data_stats = {
            'count_measurement': 10,
            'count_measurement_level': 4,
            'count_measurement_level_midnight': 1,
            'count_measurement_quality': 3,
            'count_measurement_quality_midnight': 2,
            'count_measurement_yield': 3,
            'count_measurement_yield_midnight': 0,
        }
        self.organisation.save()

        cache = self.organisation.metadata_cache

        self.assertEqual(cache.data_date_start, datetime.date(2020, 1, 1))
        self.assertEqual(cache.data_date_end, datetime.date(2021, 1, 1))
        self.assertEqual(cache.count_measurement, 10)
        self.assertEqual(cache.count_measurement_level, 4)
        self.assertEqual(cache.count_measurement_level_midnight, 1)
        self.assertEqual(cache.count_measurement_quality, 3)
        self.assertEqual(cache.count_measurement_quality_midnight, 2)
        self.assertEqual(cache.count_measurement_yield, 3)
        self.assertEqual(cache.count_measurement_yield_midnight, 0)

    def test_data_types_empty_when_no_stats(self):
        """data_types is empty when there is no measurement data."""
        self.assertEqual(self.organisation.data_types, [])

    def test_data_types_includes_level_and_quality(self):
        """data_types includes both entries when both counts are set."""
        self.organisation.data_stats = {
            'count_measurement_level': 1,
            'count_measurement_quality': 1,
        }
        self.organisation.save()
        self.assertEqual(
            self.organisation.data_types,
            ['Groundwater levels', 'Groundwater quality']
        )

    def test_data_types_level_only(self):
        """data_types only includes the level entry when only level
        measurements exist."""
        self.organisation.data_stats = {'count_measurement_level': 5}
        self.organisation.save()
        self.assertEqual(
            self.organisation.data_types, ['Groundwater levels']
        )