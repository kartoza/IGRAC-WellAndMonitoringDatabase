"""Test that MonitoringDataUploader actually persists data to the database.

gwml2/tests/test_ods_reader.py only checks that rows are *parsed* correctly
by patching `convert_record` to capture data and then raise an exception,
which means the real save path (well matching, `get_object`, `update_data`
-> `edit_well`) is never exercised there. These tests run the uploader for
real, without any mocking, and assert on the resulting DB rows.
"""
import json

from core.settings.utils import absolute_path
from gwml2.models.upload_session import (
    UploadSession, UploadSessionRowStatus
)
from gwml2.models.well import (
    WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.tasks.uploader import MonitoringDataUploader
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF, UserF, WellF


class MonitoringDataUploaderPersistenceTest(GWML2Test):
    """Test data is really saved when running MonitoringDataUploader."""

    def setUp(self):
        """Set up test data before running each test."""
        from django.core.management import call_command
        call_command("update_fixtures")

        self.organisation = OrganisationF()
        self.user = UserF()
        self.well_aa = WellF(
            original_id='1', name='AA', organisation=self.organisation
        )
        self.well_ab = WellF(
            original_id='2', name='AB', organisation=self.organisation
        )
        self.file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'monitoring_data.ods'
        )

    def create_upload_session(self, is_adding=True, is_updating=False):
        """Create upload session tied to the test organisation/user."""
        return UploadSession.objects.create(
            organisation=self.organisation,
            uploader=self.user.id,
            is_adding=is_adding,
            is_updating=is_updating
        )

    def test_monitoring_data_is_saved_to_database(self):
        """Running the uploader must persist measurements for each sheet."""
        MonitoringDataUploader(
            self.create_upload_session(), 0, 1, file_path=self.file_path
        )

        level_aa = WellLevelMeasurement.objects.get(well=self.well_aa)
        self.assertEqual(
            level_aa.parameter.name,
            'Water depth [from the ground surface]'
        )
        self.assertEqual(level_aa.value.value, 1)
        self.assertEqual(level_aa.value.unit.name, 'm')
        self.assertEqual(level_aa.methodology, 'Methodology 1')

        level_ab = WellLevelMeasurement.objects.get(well=self.well_ab)
        self.assertEqual(
            level_ab.parameter.name, 'Water level elevation a.m.s.l.'
        )
        self.assertEqual(level_ab.value.value, 2)
        self.assertEqual(level_ab.value.unit.name, 'ft')
        self.assertEqual(level_ab.methodology, 'Methodology 2')

        quality_aa = WellQualityMeasurement.objects.get(well=self.well_aa)
        self.assertEqual(quality_aa.parameter.name, 'EC')
        self.assertEqual(quality_aa.value.value, 1)
        self.assertEqual(quality_aa.value.unit.name, 'S/m')
        self.assertEqual(quality_aa.depth_value, 20)
        self.assertEqual(quality_aa.depth_unit.name, 'm')
        self.assertEqual(quality_aa.methodology, 'Methodology 3')

        quality_ab = WellQualityMeasurement.objects.get(well=self.well_ab)
        self.assertEqual(quality_ab.parameter.name, 'pH')
        self.assertEqual(quality_ab.value.value, 2)
        self.assertIsNone(quality_ab.value.unit)
        self.assertIsNone(quality_ab.depth_value)
        self.assertIsNone(quality_ab.depth_unit)
        self.assertEqual(quality_ab.methodology, 'Methodology 4')

        yield_aa = WellYieldMeasurement.objects.get(well=self.well_aa)
        self.assertEqual(yield_aa.parameter.name, 'Spring discharge')
        self.assertEqual(yield_aa.value.value, 1)
        self.assertEqual(yield_aa.value.unit.name, 'm³/h')
        self.assertEqual(yield_aa.methodology, 'Methodology 5')

        yield_ab = WellYieldMeasurement.objects.get(well=self.well_ab)
        self.assertEqual(yield_ab.parameter.name, 'Spring discharge')
        self.assertEqual(yield_ab.value.value, 2)
        self.assertEqual(yield_ab.value.unit.name, 'm³/h')
        self.assertEqual(yield_ab.methodology, 'Methodology 6')

        # Every one of the 6 data rows (2 wells x 3 sheets) should be
        # recorded as added (status=0), not skipped or errored.
        self.assertEqual(
            UploadSessionRowStatus.objects.filter(status=0).count(), 6
        )
        self.assertEqual(UploadSessionRowStatus.objects.exclude(
            status=0
        ).count(), 0)

    def test_monitoring_data_upload_skips_existing_rows_when_not_updating(
            self
    ):
        """Re-running an add-only upload must not duplicate saved rows."""
        MonitoringDataUploader(
            self.create_upload_session(), 0, 1, file_path=self.file_path
        )
        self.assertEqual(WellLevelMeasurement.objects.count(), 2)
        self.assertEqual(WellQualityMeasurement.objects.count(), 2)
        self.assertEqual(WellYieldMeasurement.objects.count(), 2)

        # A fresh session (is_adding=True, is_updating=False by default)
        # re-uploading the same file should find the existing measurements
        # via get_object() and skip them instead of creating duplicates.
        second_session = self.create_upload_session()
        MonitoringDataUploader(second_session, 0, 1, file_path=self.file_path)

        self.assertEqual(WellLevelMeasurement.objects.count(), 2)
        self.assertEqual(WellQualityMeasurement.objects.count(), 2)
        self.assertEqual(WellYieldMeasurement.objects.count(), 2)

        status = json.loads(second_session.status)
        for sheet_status in status.values():
            self.assertEqual(sheet_status['skipped'], 2)
            self.assertEqual(sheet_status['added'], 0)
            self.assertEqual(sheet_status['error'], 0)

        self.assertEqual(
            UploadSessionRowStatus.objects.filter(
                upload_session=second_session, status=2
            ).count(), 6
        )

    def test_monitoring_data_update_reuses_existing_quantity(self):
        """is_updating=True must update in place, reusing the Quantity."""
        MonitoringDataUploader(
            self.create_upload_session(), 0, 1, file_path=self.file_path
        )
        level_aa = WellLevelMeasurement.objects.get(well=self.well_aa)
        old_quantity_id = level_aa.value_id
        self.assertIsNotNone(old_quantity_id)

        # Corrupt the saved data to simulate stale values needing update.
        level_aa.value.value = 999
        level_aa.value.save()
        level_aa.methodology = 'OLD METHOD'
        level_aa.save()

        update_session = self.create_upload_session(is_updating=True)
        MonitoringDataUploader(update_session, 0, 1, file_path=self.file_path)

        # No duplicate row created; the same measurement was updated.
        self.assertEqual(WellLevelMeasurement.objects.count(), 2)
        level_aa.refresh_from_db()
        self.assertEqual(level_aa.value_id, old_quantity_id)
        self.assertEqual(level_aa.value.value, 1)
        self.assertEqual(level_aa.methodology, 'Methodology 1')

        status = json.loads(update_session.status)
        self.assertEqual(status['Groundwater Level']['added'], 2)
        self.assertEqual(status['Groundwater Level']['skipped'], 0)
        self.assertEqual(status['Groundwater Level']['error'], 0)

    def test_monitoring_data_update_creates_quantity_when_missing(self):
        """is_updating=True must attach a new Quantity if none existed."""
        MonitoringDataUploader(
            self.create_upload_session(), 0, 1, file_path=self.file_path
        )
        level_aa = WellLevelMeasurement.objects.get(well=self.well_aa)
        level_aa.value_id = None
        level_aa.save()
        level_aa.refresh_from_db()
        self.assertIsNone(level_aa.value_id)

        update_session = self.create_upload_session(is_updating=True)
        MonitoringDataUploader(update_session, 0, 1, file_path=self.file_path)

        self.assertEqual(WellLevelMeasurement.objects.count(), 2)
        level_aa.refresh_from_db()
        self.assertIsNotNone(level_aa.value_id)
        self.assertEqual(level_aa.value.value, 1)
        self.assertEqual(level_aa.value.unit.name, 'm')
