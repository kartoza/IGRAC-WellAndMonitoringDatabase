"""Test ODS Reader."""

from gwml2.models.general import Quantity
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well
from gwml2.models.well_deletion import WellDeletion
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    WellF, OrganisationF, UserF,
    WellLevelMeasurementF, WellQualityMeasurementF, WellYieldMeasurementF
)


class WellDeletionTest(GWML2Test):
    """Test Well Deletion."""

    def setUp(self):
        """To setup test."""
        self.original_id = 'Well.1'
        self.parameter = TermMeasurementParameter.objects.create()

        self.admin = UserF()
        self.editor = UserF()
        self.viewer = UserF()

        self.organisation = OrganisationF(
            admins=[self.admin.id],
            editors=[self.editor.id]
        )

        self.well_1 = WellF(
            organisation=self.organisation,
            name='Well 1',
            original_id=self.original_id
        )
        WellLevelMeasurementF(well=self.well_1, parameter=self.parameter)
        WellLevelMeasurementF(well=self.well_1, parameter=self.parameter)
        WellQualityMeasurementF(well=self.well_1, parameter=self.parameter)
        WellQualityMeasurementF(well=self.well_1, parameter=self.parameter)
        WellYieldMeasurementF(well=self.well_1, parameter=self.parameter)
        WellYieldMeasurementF(well=self.well_1, parameter=self.parameter)

        self.well_2 = WellF(
            organisation=self.organisation,
            name='Well 2',
            original_id=self.original_id
        )
        WellLevelMeasurementF(well=self.well_2, parameter=self.parameter)
        WellQualityMeasurementF(well=self.well_2, parameter=self.parameter)
        WellYieldMeasurementF(well=self.well_2, parameter=self.parameter)

    def test_well_deletion(self):
        """To well deletion."""
        self.assertEqual(Well.objects.count(), 2)
        self.assertEqual(Quantity.objects.count(), 9)
        self.assertEqual(self.well_1.number_of_measurements, 6)
        self.assertEqual(self.well_1.number_of_measurements_level, 2)
        self.assertEqual(self.well_1.number_of_measurements_quality, 2)
        self.assertEqual(self.well_1.number_of_measurements_yield, 2)
        self.assertEqual(self.well_2.number_of_measurements, 3)
        self.assertEqual(self.well_2.number_of_measurements_level, 1)
        self.assertEqual(self.well_2.number_of_measurements_quality, 1)
        self.assertEqual(self.well_2.number_of_measurements_yield, 1)

        well_deletion = WellDeletion.objects.create(
            ids=[self.well_1.id], data={}
        )
        well_deletion.run()

        with self.assertRaises(Well.DoesNotExist):
            self.well_1.refresh_from_db()

        self.well_2.refresh_from_db()
        self.assertEqual(Well.objects.count(), 1)
        self.assertEqual(Quantity.objects.count(), 3)
        self.assertEqual(self.well_2.number_of_measurements, 3)
        self.assertEqual(self.well_2.number_of_measurements_level, 1)
        self.assertEqual(self.well_2.number_of_measurements_quality, 1)
        self.assertEqual(self.well_2.number_of_measurements_yield, 1)
