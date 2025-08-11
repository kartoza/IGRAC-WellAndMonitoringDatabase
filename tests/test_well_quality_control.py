"""Test Well Quality Control."""

import json

from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter, TermMeasurementParameterGroup
)
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    WellF, WellLevelMeasurementF,
    WellQualityMeasurementF, WellYieldMeasurementF
)


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
        self.unit = Unit.objects.create(name='m')
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2019-01-01 00:00:00',
            value=Quantity.objects.create(value=1, unit=self.unit)
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2020-01-01 00:00:00',
            value=Quantity.objects.create(value=60, unit=self.unit)
        )
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2025-01-01 00:00:00',
            value=Quantity.objects.create(value=6, unit=self.unit)
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
            value=Quantity.objects.create(value=1, unit=self.unit)
        )
        WellLevelMeasurementF(
            well=self.well_2, parameter=self.parameter,
            time='2020-01-02 00:00:00',
            value=Quantity.objects.create(value=2, unit=self.unit)
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

    def test_time_quality_control(self):
        """To gap quality control."""
        self.well_1.quality_control.gap_time_quality()
        self.well_2.quality_control.gap_time_quality()

        self.assertTrue(
            f'"gap": 1827.0, "current": "2025-01-01 00:00:00", "previous": "2020-01-01 00:00:00", "parameter_id": {self.parameter.id}' in
            json.dumps(self.well_1.quality_control.groundwater_level_time_gap)
        )
        self.assertIsNotNone(
            self.well_1.quality_control.groundwater_level_time_gap_generated_time
        )
        self.assertIsNone(
            self.well_2.quality_control.groundwater_level_time_gap)
        self.assertIsNotNone(
            self.well_2.quality_control.groundwater_level_time_gap_generated_time
        )

    def test_level_quality_control(self):
        """To gap quality control."""
        self.well_1.quality_control.gap_level_quality()
        self.well_2.quality_control.gap_level_quality()
        self.well_1.refresh_from_db()
        self.well_2.refresh_from_db()

        self.assertTrue(
            f'"gap": 59.0, "time": "2020-01-01 00:00:00", "current": 60.0, "previous": 1.0, "parameter_id": {self.parameter.id}' in
            json.dumps(self.well_1.quality_control.groundwater_level_value_gap)
        )
        self.assertIsNotNone(
            self.well_1.quality_control.groundwater_level_value_gap_generated_time
        )
        self.assertIsNone(
            self.well_2.quality_control.groundwater_level_value_gap
        )
        self.assertIsNotNone(
            self.well_2.quality_control.groundwater_level_value_gap_generated_time
        )

    def test_strange_value(self):
        """To gap quality control."""
        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2019-01-02 00:00:00',
            value=Quantity.objects.create(value=0, unit=self.unit)
        )

        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2019-01-03 00:00:00',
            value=Quantity.objects.create(value=-9999, unit=self.unit)
        )

        WellLevelMeasurementF(
            well=self.well_1, parameter=self.parameter,
            time='2019-01-04 00:00:00',
            value=Quantity.objects.create(value=-100, unit=self.unit)
        )

        self.well_1.quality_control.strange_value_quality()
        self.well_2.quality_control.strange_value_quality()
        self.well_1.refresh_from_db()
        self.well_2.refresh_from_db()
        self.assertTrue(
            f'"time": "2019-01-02 00:00:00", "value": 0.0, "parameter_id": {self.parameter.id}' in
            json.dumps(
                self.well_1.quality_control.groundwater_level_strange_value
            )
        )
        self.assertTrue(
            f'"time": "2019-01-03 00:00:00", "value": -9999.0, "parameter_id": {self.parameter.id}' in
            json.dumps(
                self.well_1.quality_control.groundwater_level_strange_value
            )
        )
        self.assertIsNotNone(
            self.well_1.quality_control.groundwater_level_strange_value_generated_time
        )
        self.assertIsNone(
            self.well_2.quality_control.groundwater_level_strange_value
        )
        self.assertIsNotNone(
            self.well_2.quality_control.groundwater_level_strange_value_generated_time
        )
