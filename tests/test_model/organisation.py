"""Test for Organisation model."""

from unittest.mock import patch

from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF, UserF, WellF


class OrganisationTest(GWML2Test):
    """Test for Organisation model."""

    def setUp(self):
        """To setup test."""
        self.name = 'Organisation 1'
        self.admin = UserF()
        self.editor = UserF()
        self.viewer = UserF()

    def test_create(self):
        """Test create."""
        organisation = OrganisationF(name=self.name)
        self.assertEquals(organisation.name, self.name)

    def test_access(self):
        """Test access."""
        organisation = OrganisationF(
            name=self.name,
            admins=[self.admin.id],
            editors=[self.editor.id]
        )

        self.assertTrue(organisation.is_admin(self.admin))
        self.assertFalse(organisation.is_admin(self.editor))
        self.assertFalse(organisation.is_admin(self.viewer))

        self.assertTrue(organisation.is_editor(self.editor))
        self.assertTrue(organisation.is_editor(self.editor))
        self.assertFalse(organisation.is_editor(self.viewer))

    @patch(
        'gwml2.models.well_management.organisation.Organisation.update_ggis_uid'
    )
    def test_change_ggis_uid_being_called(self, mock_update_ggis_uid):
        """Test change ggis uid."""
        organisation = OrganisationF(
            name='Organisation A',
            admins=[],
            editors=[]
        )
        self.assertEqual(mock_update_ggis_uid.call_count, 0)
        organisation.name = 'Organisation B'
        organisation.save()
        self.assertEqual(mock_update_ggis_uid.call_count, 1)
        organisation.order = 100
        organisation.save()
        self.assertEqual(mock_update_ggis_uid.call_count, 1)
        organisation.name = 'Organisation A'
        organisation.save()
        self.assertEqual(mock_update_ggis_uid.call_count, 2)

    def test_change_ggis_uid(self):
        """Test change ggis uid."""
        organisation = OrganisationF(
            name='Organisation AA',
            admins=[],
            editors=[]
        )
        organisation_2 = OrganisationF(
            name='Organisation BA',
            admins=[],
            editors=[]
        )
        well = WellF(original_id='Well A', organisation=organisation)
        well_2 = WellF(original_id='Well B', organisation=organisation_2)
        self.assertEqual(well.ggis_uid, 'Organisation AA-Well A')
        self.assertEqual(well_2.ggis_uid, 'Organisation BA-Well B')
        organisation.name = 'Organisation AB'
        organisation.save()
        well.refresh_from_db()
        well_2.refresh_from_db()
        self.assertEqual(well.ggis_uid, 'Organisation AB-Well A')
        self.assertEqual(well_2.ggis_uid, 'Organisation BA-Well B')
        organisation_2.name = 'Organisation BB'
        organisation_2.save()
        well.refresh_from_db()
        well_2.refresh_from_db()
        self.assertEqual(well.ggis_uid, 'Organisation AB-Well A')
        self.assertEqual(well_2.ggis_uid, 'Organisation BB-Well B')
