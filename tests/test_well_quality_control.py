"""Test Well Quality Control."""

from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter, TermMeasurementParameterGroup
)
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    WellF, WellLevelMeasurementF,
    WellQualityMeasurementF, WellYieldMeasurementF
)
from gwml2.utils.well_quality_control import WellQualityControl


class TestWellQualityControl(GWML2Test):
    """Test well quality control test."""

    def setUp(self):
        """To setup test."""
        self.original_id = 'Well.1'
        self.parameter = TermMeasurementParameter.objects.create(
            name='Term 1'
        )
        self.parameter_2 = TermMeasurementParameter.objects.create(
            name='Term 2'
        )
        self.parameter_3 = TermMeasurementParameter.objects.create(
            name='Term 3'
        )
        self.parameter_4 = TermMeasurementParameter.objects.create(
            name='Term 4'
        )
        self.parameter_5 = TermMeasurementParameter.objects.create(
            name='Term 5'
        )
        self.parameter_6 = TermMeasurementParameter.objects.create(
            name='Term 6'
        )
        group_level = TermMeasurementParameterGroup.objects.create(
            name='Level Measurement'
        )
        group_quality = TermMeasurementParameterGroup.objects.create(
            name='Quality Measurement'
        )
        yield_quality = TermMeasurementParameterGroup.objects.create(
            name='Yield Measurement'
        )
        group_level.parameters.add(self.parameter)
        group_quality.parameters.add(self.parameter_2)
        group_quality.parameters.add(self.parameter_3)
        yield_quality.parameters.add(self.parameter_4)
        yield_quality.parameters.add(self.parameter_5)

        self.well_1 = WellF(
            name='Well 1',
            original_id=self.original_id
        )
        unit = Unit.objects.create(name='m')
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2019-01-01 00:00:00',
            value=Quantity.objects.create(value=1, unit=unit)
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2020-01-01 00:00:00',
            value=Quantity.objects.create(value=60, unit=unit)
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2025-01-01 00:00:00',
            value=Quantity.objects.create(value=6, unit=unit)
        )

        WellQualityMeasurementF(
            well=self.well_1, parameter=self.parameter_2,
            time='2020-01-01 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_1, parameter=self.parameter_2,
            time='2026-01-01 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_1, parameter=self.parameter_3,
            time='2020-01-01 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_1, parameter=self.parameter_3,
            time='2021-01-02 00:00:00'
        )

        WellYieldMeasurementF(
            well=self.well_1, parameter=self.parameter_4,
            time='2020-01-01 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_1, parameter=self.parameter_4,
            time='2024-01-01 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_1, parameter=self.parameter_5,
            time='2020-01-01 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_1, parameter=self.parameter_5,
            time='2021-01-02 00:00:00'
        )

        self.well_2 = WellF(
            name='Well 2',
            original_id=self.original_id
        )
        WellLevelMeasurementF(
            well=self.well_2, parameter=self.parameter,
            time='2020-01-01 00:00:00',
            value=Quantity.objects.create(value=1, unit=unit)
        )
        WellLevelMeasurementF(
            well=self.well_2, parameter=self.parameter,
            time='2020-01-02 00:00:00',
            value=Quantity.objects.create(value=2, unit=unit)
        )

        WellQualityMeasurementF(
            well=self.well_2, parameter=self.parameter_2,
            time='2020-01-01 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_2, parameter=self.parameter_2,
            time='2021-01-02 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_2, parameter=self.parameter_3,
            time='2020-01-01 00:00:00'
        )
        WellQualityMeasurementF(
            well=self.well_2, parameter=self.parameter_3,
            time='2021-01-02 00:00:00'
        )

        WellYieldMeasurementF(
            well=self.well_2, parameter=self.parameter_4,
            time='2020-01-01 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_2, parameter=self.parameter_4,
            time='2021-01-02 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_2, parameter=self.parameter_5,
            time='2020-01-01 00:00:00'
        )
        WellYieldMeasurementF(
            well=self.well_2, parameter=self.parameter_5,
            time='2021-01-02 00:00:00'
        )

    def test_gap_quality_control(self):
        """To gap quality control."""
        WellQualityControl(self.well_1).gap_time_quality()
        WellQualityControl(self.well_2).gap_time_quality()
        self.well_1.refresh_from_db()
        self.well_2.refresh_from_db()

        self.assertTrue(
            f'"parameter_id": {self.parameter.id}, "current": "2025-01-01 00:00:00", "previous": "2020-01-01 00:00:00", "gap": 1827.0' in self.well_1.bad_quality_time_gap
        )
        self.assertTrue(
            f'"parameter_id": {self.parameter_2.id}, "current": "2026-01-01 00:00:00", "previous": "2020-01-01 00:00:00", "gap": 2192.0' in self.well_1.bad_quality_time_gap
        )
        self.assertTrue(
            f'"parameter_id": {self.parameter_4.id}, "current": "2024-01-01 00:00:00", "previous": "2020-01-01 00:00:00", "gap": 1461.0' in self.well_1.bad_quality_time_gap
        )
        self.assertIsNotNone(self.well_1.bad_quality_time_gap_generated_time)
        self.assertIsNone(self.well_2.bad_quality_time_gap)
        self.assertIsNotNone(self.well_2.bad_quality_time_gap_generated_time)

    def test_level_quality_control(self):
        """To gap quality control."""
        WellQualityControl(self.well_1).gap_level_quality()
        WellQualityControl(self.well_2).gap_level_quality()
        self.well_1.refresh_from_db()
        self.well_2.refresh_from_db()

        self.assertTrue(
            f'"parameter_id": {self.parameter.id}, "current": 60.0, "previous": 1.0, "gap": 59.0' in self.well_1.bad_quality_level_gap
        )
        self.assertIsNotNone(self.well_1.bad_quality_level_gap_generated_time)
        self.assertIsNone(self.well_2.bad_quality_level_gap)
        self.assertIsNotNone(self.well_2.bad_quality_level_gap_generated_time)
