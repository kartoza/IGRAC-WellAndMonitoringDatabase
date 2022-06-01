"""Test for Well model."""

from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import WellF, OrganisationF, UserF


class WellTest(GWML2Test):
    """Test for Well model."""

    def setUp(self):
        """To setup test."""
        self.name = 'Well 1'
        self.original_id = 'Well.1'

        self.admin = UserF()
        self.editor = UserF()
        self.viewer = UserF()

        self.organisation = OrganisationF(
            admins=[self.admin.id],
            editors=[self.editor.id]
        )

    def test_create(self):
        """Test create."""
        well = WellF(
            organisation=self.organisation,
            name=self.name,
            original_id=self.original_id
        )
        self.assertEquals(well.original_id, self.original_id)
        self.assertEquals(well.name, self.name)
        self.assertEquals(
            well.ggis_uid, f'{self.organisation.name}-{self.original_id}'
        )

    def test_view_access_public(self):
        """ Test view well access. """
        well = WellF(
            organisation=self.organisation,
            name=self.name,
            original_id=self.original_id
        )
        self.assertTrue(well.view_permission(self.viewer))

    def test_view_access_private(self):
        """ Test view well access. """
        well = WellF(
            public=False,
            organisation=self.organisation,
            name=self.name,
            original_id=self.original_id
        )
        self.assertFalse(well.view_permission(self.viewer))
        self.assertTrue(well.view_permission(self.admin))
        self.assertTrue(well.view_permission(self.editor))

    def test_edit_access_public(self):
        """ Test edit well access. """
        well = WellF(
            organisation=self.organisation,
            name=self.name,
            original_id=self.original_id
        )
        self.assertFalse(well.editor_permission(self.viewer))

    def test_edit_access_private(self):
        """ Test edit well access. """
        well = WellF(
            organisation=self.organisation,
            name=self.name,
            original_id=self.original_id
        )
        self.assertFalse(well.editor_permission(self.viewer))
        self.assertTrue(well.editor_permission(self.admin))
        self.assertTrue(well.editor_permission(self.editor))
