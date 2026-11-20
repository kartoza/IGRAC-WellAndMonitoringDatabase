"""Test skipping cache step when other upload session is running."""

from datetime import timedelta

from django.utils import timezone

from gwml2.models.general import Country
from gwml2.models.upload_session import (
    UploadSession,
    UploadSessionCheckpoint,
    UploadSessionCheckpointLog,
)
from gwml2.models.well_management.organisation import Organisation
from gwml2.tasks.uploader.uploader import (
    SKIPPED_BY_OTHER_SESSION_STEP,
    StepCheckpoint,
)
from gwml2.tests.base import GWML2Test

CACHE_WELLS = UploadSessionCheckpoint.get_index(UploadSessionCheckpoint.CACHE_WELLS)
CACHE_COUNTRY = UploadSessionCheckpoint.get_index(UploadSessionCheckpoint.CACHE_COUNTRY)
CACHE_ORGANISATION = UploadSessionCheckpoint.get_index(
    UploadSessionCheckpoint.CACHE_ORGANISATION
)


class UploadSessionSkipCacheTest(GWML2Test):
    """Test StepCheckpoint skip for country and organisation cache."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(name='Country A', code='CA')
        self.other_country = Country.objects.create(name='Country B', code='CB')
        self.organisation = Organisation.objects.create(
            name='Organisation 1', country=self.country
        )
        self.organisation_same_country = Organisation.objects.create(
            name='Organisation 2', country=self.country
        )
        self.organisation_other_country = Organisation.objects.create(
            name='Organisation 3', country=self.other_country
        )

    def create_session(self, organisation, checkpoint=CACHE_WELLS, **kwargs):
        """Create upload session."""
        return UploadSession.objects.create(
            organisation=organisation, checkpoint=checkpoint, retry=1, **kwargs
        )

    def enter(self, step_name, session):
        """Enter the step and return the checkpoint."""
        with StepCheckpoint(step_name, upload_session=session) as checkpoint:
            return checkpoint

    def test_no_other_session(self):
        """Step is not skipped when there is no other session."""
        session = self.create_session(self.organisation)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)
        self.assertFalse(
            self.enter(UploadSessionCheckpoint.CACHE_ORGANISATION, session).skip
        )

    def test_skip_country_same_country(self):
        """Country cache is skipped for other session in same country."""
        self.create_session(self.organisation_same_country)
        session = self.create_session(self.organisation)
        checkpoint = self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session)
        self.assertTrue(checkpoint.skip)

        # Checkpoint is moved to this step, so other session sees it
        session.refresh_from_db()
        self.assertEqual(session.checkpoint, CACHE_COUNTRY)

        log = UploadSessionCheckpointLog.objects.get(
            upload_session=session, checkpoint=CACHE_COUNTRY, retry=1
        )
        self.assertEqual(log.step, SKIPPED_BY_OTHER_SESSION_STEP)
        self.assertIsNotNone(log.finish_at)

        # Organisation is different, so organisation cache is not skipped
        self.assertFalse(
            self.enter(UploadSessionCheckpoint.CACHE_ORGANISATION, session).skip
        )

    def test_not_skip_country_other_country(self):
        """Country cache is not skipped for other session in other country."""
        self.create_session(self.organisation_other_country)
        session = self.create_session(self.organisation)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)

    def test_skip_organisation_same_organisation(self):
        """Organisation cache is skipped for other session in same organisation."""
        self.create_session(self.organisation)
        session = self.create_session(self.organisation, checkpoint=CACHE_COUNTRY)
        checkpoint = self.enter(UploadSessionCheckpoint.CACHE_ORGANISATION, session)
        self.assertTrue(checkpoint.skip)

    def test_not_skip_other_session_already_passed(self):
        """Not skipped when other session already passed this step."""
        self.create_session(self.organisation, checkpoint=CACHE_ORGANISATION)
        session = self.create_session(self.organisation)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)

    def test_not_skip_other_session_finished(self):
        """Not skipped when other session is processed or canceled."""
        self.create_session(self.organisation, is_processed=True)
        self.create_session(self.organisation, is_canceled=True)
        session = self.create_session(self.organisation)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)
        self.assertFalse(
            self.enter(UploadSessionCheckpoint.CACHE_ORGANISATION, session).skip
        )

    def test_not_skip_other_session_stuck(self):
        """Not skipped when other session is too old (stuck)."""
        self.create_session(
            self.organisation, uploaded_at=timezone.now() - timedelta(days=30)
        )
        session = self.create_session(self.organisation)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)

    def test_not_skip_without_organisation(self):
        """Not skipped when session has no organisation."""
        self.create_session(None)
        session = self.create_session(None)
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session).skip)
        self.assertFalse(
            self.enter(UploadSessionCheckpoint.CACHE_ORGANISATION, session).skip
        )

    def test_two_sessions_do_not_both_skip(self):
        """When both reach country step, only the first one skips."""
        session_a = self.create_session(self.organisation)
        session_b = self.create_session(self.organisation)

        # A reaches country step while B is still in cache wells
        self.assertTrue(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session_a).skip)

        # B reaches country step, A already on country step -> B runs it
        self.assertFalse(self.enter(UploadSessionCheckpoint.CACHE_COUNTRY, session_b).skip)
