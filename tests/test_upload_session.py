"""Test Upload."""

import json
import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files import File

from core.settings.utils import absolute_path
from gwml2.models.upload_session import (
    UploadSession, UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UploadSessionCheckpoint
)
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.tests.base import GWML2Test


def mock_function(self):
    """Return mock function."""
    pass


def mock_generate_data_well_cache_side_effect(*args, **kwargs):
    """Custom function to mock `generate_data_well_cache`."""
    well = Well.objects.get(id=kwargs['well_id'])
    well_ids = list(Well.objects.values_list('id', flat=True).order_by('id'))
    if well_ids.index(well.id) == 2:
        raise Exception('Error')


def mock_generate_data_well_cache_side_effect_normal(*args, **kwargs):
    """Custom function to mock `generate_data_well_cache`."""
    pass


def mock_generate_data_country_cache_side_effect(*args, **kwargs):
    """Custom function to mock `generate_data_well_cache`."""
    if args[0] == 'USA':
        raise Exception('Error')


def mock_generate_data_country_cache_side_effect_normal(*args, **kwargs):
    """Custom function to mock `generate_data_well_cache`."""
    pass


class UploadSessionTest(GWML2Test):
    """Test UploadSession tests."""

    def setUp(self):
        """Set up test data before running each test."""
        from django.core.management import call_command
        call_command("update_fixtures")

        self.user = get_user_model().objects.create_user(
            username='testuser'
        )

        self.organisation = Organisation.objects.create(
            name='Test Organisation',
        )

    def tearDown(self):
        """Stop the patcher."""
        super().tearDown()

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_full_run(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        mock_generate_data_well_cache.return_value = None
        mock_generate_data_country_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id
            )
            session.run()
            self.assertEquals(Well.objects.count(), 4)
            self.assertEqual(mock_generate_data_well_cache.call_count, 4)
            self.assertEqual(mock_generate_data_country_cache.call_count, 2)
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 1
            )
            mock_create_report_excel.assert_called_once()
            mock_run_istsos_cache.assert_called_once()

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.FINISH
                )
            )
            self.assertEquals(session.step, 'Finish')
            self.assertEquals(
                json.loads(session.status),
                {
                    "General Information": {
                        "added": 4, "error": 0, "skipped": 0
                    },
                    "Hydrogeology": {"added": 2, "error": 0, "skipped": 0}
                }
            )

            self.assertEquals(session.progress, 100)

        # ---------------------------------------
        # Restart
        # ---------------------------------------
        session.run(True)
        self.assertEquals(Well.objects.count(), 4)
        self.assertEqual(mock_generate_data_well_cache.call_count, 4)
        self.assertEqual(mock_generate_data_country_cache.call_count, 2)
        self.assertEqual(
            mock_generate_data_organisation_cache.call_count, 1
        )
        self.assertEqual(
            mock_create_report_excel.call_count, 2
        )
        self.assertEqual(
            mock_run_istsos_cache.call_count, 2
        )
        self.assertEquals(
            session.checkpoint, UploadSessionCheckpoint.get_index(
                UploadSessionCheckpoint.FINISH
            )
        )
        self.assertEquals(session.step, 'Finish')
        self.assertEquals(
            json.loads(session.status),
            {
                "General Information": {
                    "added": 0, "error": 0, "skipped": 4
                },
                "Hydrogeology": {"added": 0, "error": 0, "skipped": 2}
            }
        )

        self.assertEquals(session.progress, 100)

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_resume_on_saving_data(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        mock_generate_data_well_cache.return_value = None
        mock_generate_data_country_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id,
                status=json.dumps(
                    {
                        "General Information": {
                            "added": 0, "error": 0, "skipped": 2
                        },
                        "Hydrogeology": {
                            "added": 0, "error": 0, "skipped": 2
                        }
                    }
                )
            )
            session.run()
            self.assertEquals(Well.objects.count(), 2)
            self.assertEqual(mock_generate_data_well_cache.call_count, 2)
            self.assertEqual(mock_generate_data_country_cache.call_count, 1)
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 1
            )
            mock_create_report_excel.assert_called_once()
            mock_run_istsos_cache.assert_called_once()

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.FINISH
                )
            )
            self.assertEquals(session.step, 'Finish')
            self.assertEquals(
                json.loads(session.status),
                {
                    "General Information": {
                        "added": 2, "error": 0, "skipped": 2
                    },
                    "Hydrogeology": {"added": 0, "error": 0, "skipped": 2}
                }
            )

            self.assertEquals(session.progress, 100)

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_resume_cache_wells(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        Well.objects.all().delete()

        mock_generate_data_country_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        mock_generate_data_well_cache.side_effect = (
            mock_generate_data_well_cache_side_effect
        )

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id
            )
            session.run()
            self.assertEquals(Well.objects.count(), 4)
            self.assertEqual(mock_generate_data_well_cache.call_count, 3)
            self.assertEqual(mock_generate_data_country_cache.call_count, 0)
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 0
            )
            self.assertEqual(mock_create_report_excel.call_count, 0)
            self.assertEqual(mock_run_istsos_cache.call_count, 0)

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.CACHE_WELLS
                )
            )
            self.assertEquals(
                session.status,
                'Error'
            )

            self.assertEquals(session.progress, 100)

        # ---------------------------------------
        # Resume with middle wells cache
        # ---------------------------------------
        mock_generate_data_well_cache.side_effect = (
            mock_generate_data_well_cache_side_effect_normal
        )
        session.run()
        self.assertEquals(Well.objects.count(), 4)
        self.assertEqual(mock_generate_data_country_cache.call_count, 2)
        self.assertEqual(
            mock_generate_data_organisation_cache.call_count, 1
        )
        self.assertEqual(
            mock_create_report_excel.call_count, 1
        )
        self.assertEqual(
            mock_run_istsos_cache.call_count, 1
        )
        self.assertEquals(
            session.checkpoint, UploadSessionCheckpoint.get_index(
                UploadSessionCheckpoint.FINISH
            )
        )
        self.assertEquals(session.step, 'Finish')
        self.assertEquals(session.progress, 100)

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_resume_country_cache(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        mock_generate_data_well_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        mock_generate_data_country_cache.side_effect = (
            mock_generate_data_country_cache_side_effect
        )

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id
            )
            session.run()
            self.assertEquals(Well.objects.count(), 4)
            self.assertEqual(mock_generate_data_well_cache.call_count, 4)
            self.assertEqual(mock_generate_data_country_cache.call_count, 2)
            self.assertEqual(session.checkpoint_ids, ['IDN'])
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 0
            )
            self.assertEqual(mock_create_report_excel.call_count, 0)
            self.assertEqual(mock_run_istsos_cache.call_count, 0)

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.CACHE_COUNTRY
                )
            )
            self.assertEquals(
                session.step, "Running country cache : ['IDN', 'USA']"
            )
            self.assertEquals(session.progress, 100)

        # ---------------------------------------
        # Resume with middle country
        # ---------------------------------------
        mock_generate_data_country_cache.side_effect = (
            mock_generate_data_country_cache_side_effect_normal
        )
        session.run()
        self.assertEqual(session.checkpoint_ids, [])
        self.assertEquals(Well.objects.count(), 4)
        self.assertEqual(mock_generate_data_well_cache.call_count, 4)
        self.assertEqual(mock_generate_data_country_cache.call_count, 3)
        self.assertEqual(
            mock_generate_data_organisation_cache.call_count, 1
        )
        self.assertEqual(
            mock_create_report_excel.call_count, 1
        )
        self.assertEqual(
            mock_run_istsos_cache.call_count, 1
        )
        self.assertEquals(
            session.checkpoint, UploadSessionCheckpoint.get_index(
                UploadSessionCheckpoint.FINISH
            )
        )
        self.assertEquals(session.step, 'Finish')
        self.assertEquals(session.progress, 100)

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_resume_organisation_cache(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        mock_generate_data_well_cache.return_value = None
        mock_generate_data_country_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id
            )
            session.run()
            self.assertEquals(Well.objects.count(), 4)
            self.assertEqual(mock_generate_data_well_cache.call_count, 4)
            self.assertEqual(mock_generate_data_country_cache.call_count, 2)
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 1
            )
            mock_create_report_excel.assert_called_once()
            mock_run_istsos_cache.assert_called_once()

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.FINISH
                )
            )
            self.assertEquals(session.step, 'Finish')
            self.assertEquals(
                json.loads(session.status),
                {
                    "General Information": {
                        "added": 4, "error": 0, "skipped": 0
                    },
                    "Hydrogeology": {"added": 2, "error": 0, "skipped": 0}
                }
            )

            self.assertEquals(session.progress, 100)

        # ---------------------------------------
        # Resume with middle country
        # ---------------------------------------
        session.checkpoint = UploadSessionCheckpoint.get_index(
            UploadSessionCheckpoint.CACHE_ORGANISATION
        )
        session.save()
        session.run()
        self.assertEquals(Well.objects.count(), 4)
        self.assertEqual(mock_generate_data_well_cache.call_count, 4)
        self.assertEqual(mock_generate_data_country_cache.call_count, 2)
        self.assertEqual(
            mock_generate_data_organisation_cache.call_count, 2
        )
        self.assertEqual(
            mock_create_report_excel.call_count, 2
        )
        self.assertEqual(
            mock_run_istsos_cache.call_count, 2
        )
        self.assertEquals(
            session.checkpoint, UploadSessionCheckpoint.get_index(
                UploadSessionCheckpoint.FINISH
            )
        )
        self.assertEquals(session.step, 'Finish')
        self.assertEquals(
            json.loads(session.status),
            {
                "General Information": {
                    "added": 4, "error": 0, "skipped": 0
                },
                "Hydrogeology": {"added": 2, "error": 0, "skipped": 0}
            }
        )

        self.assertEquals(session.progress, 100)

    @patch('gwml2.models.upload_session.UploadSession.create_report_excel')
    @patch('gwml2.tasks.uploader.uploader.BatchUploader.run_istsos_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_well_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_country_cache')
    @patch('gwml2.tasks.uploader.uploader.generate_data_organisation_cache')
    def test_resume_create_report(
            self,
            mock_generate_data_organisation_cache,
            mock_generate_data_country_cache,
            mock_generate_data_well_cache,
            mock_run_istsos_cache,
            mock_create_report_excel
    ):
        """To file exist."""
        mock_generate_data_well_cache.return_value = None
        mock_generate_data_country_cache.return_value = None
        mock_generate_data_organisation_cache.return_value = None
        mock_run_istsos_cache.return_value = None
        mock_create_report_excel.return_value = None

        file_path = absolute_path(
            'gwml2', 'tests', 'fixtures', 'wells.test.ods'
        )
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            django_file = File(f, name=filename)
            session = UploadSession.objects.create(
                organisation=self.organisation,
                category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                upload_file=django_file,
                uploader=self.user.id
            )
            session.run()
            self.assertEquals(Well.objects.count(), 4)
            self.assertEqual(mock_generate_data_well_cache.call_count, 4)
            self.assertEqual(mock_generate_data_country_cache.call_count, 2)
            self.assertEqual(
                mock_generate_data_organisation_cache.call_count, 1
            )
            mock_create_report_excel.assert_called_once()
            mock_run_istsos_cache.assert_called_once()

            self.assertEquals(
                session.checkpoint, UploadSessionCheckpoint.get_index(
                    UploadSessionCheckpoint.FINISH
                )
            )
            self.assertEquals(session.step, 'Finish')
            self.assertEquals(
                json.loads(session.status),
                {
                    "General Information": {
                        "added": 4, "error": 0, "skipped": 0
                    },
                    "Hydrogeology": {"added": 2, "error": 0, "skipped": 0}
                }
            )

            self.assertEquals(session.progress, 100)

        # ---------------------------------------
        # Resume with middle country
        # ---------------------------------------
        session.checkpoint = UploadSessionCheckpoint.get_index(
            UploadSessionCheckpoint.CREATE_REPORT
        )
        session.save()
        session.run()
        self.assertEquals(Well.objects.count(), 4)
        self.assertEqual(mock_generate_data_well_cache.call_count, 4)
        self.assertEqual(mock_generate_data_country_cache.call_count, 2)
        self.assertEqual(
            mock_generate_data_organisation_cache.call_count, 1
        )
        self.assertEqual(
            mock_create_report_excel.call_count, 2
        )
        self.assertEqual(
            mock_run_istsos_cache.call_count, 2
        )
        self.assertEquals(
            session.checkpoint, UploadSessionCheckpoint.get_index(
                UploadSessionCheckpoint.FINISH
            )
        )
        self.assertEquals(session.step, 'Finish')
        self.assertEquals(
            json.loads(session.status),
            {
                "General Information": {
                    "added": 4, "error": 0, "skipped": 0
                },
                "Hydrogeology": {"added": 2, "error": 0, "skipped": 0}
            }
        )

        self.assertEquals(session.progress, 100)
