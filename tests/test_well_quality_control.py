"""Test Well Quality Control."""

from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    WellF, WellLevelMeasurementF
)
from gwml2.utils.well_quality_control import WellQualityControl


class TestWellQualityControl(GWML2Test):
    """Test well quality control test."""

    def setUp(self):
        """To setup test."""
        self.original_id = 'Well.1'
        self.parameter = TermMeasurementParameter.objects.create()

        self.well_1 = WellF(
            name='Well 1',
            original_id=self.original_id
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2020-01-01 00:00:00'
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2025-01-01 00:00:00'
        )

        self.well_2 = WellF(
            name='Well 2',
            original_id=self.original_id
        )
        WellLevelMeasurementF(
            well=self.well_2, parameter=self.parameter,
            time='2020-01-01 00:00:00'
        )
        WellLevelMeasurementF(
            well=self.well_2, parameter=self.parameter,
            time='2020-01-02 00:00:00'
        )

    def test_gap_quality_control(self):
        """To gap quality control."""
        WellQualityControl(self.well_1).gap_time_quality()
        WellQualityControl(self.well_2).gap_time_quality()
        self.well_1.refresh_from_db()
        self.well_2.refresh_from_db()

        self.assertTrue(
            '"gap_in_days": 1827.0' in self.well_1.bad_quality_time_gap
        )
        self.assertIsNotNone(self.well_1.bad_quality_time_gap_generated_time)
        self.assertIsNone(self.well_2.bad_quality_time_gap)
        self.assertIsNotNone(self.well_2.bad_quality_time_gap_generated_time)
