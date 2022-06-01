"""Test for Organisation model."""

from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF, UserF


class OrganisationTest(GWML2Test):
    """Test for Organisation model."""
    databases = '__all__'

    def setUp(self):
        """To setup test."""
        self.name = 'Organisation 1'
        self.admin = UserF()
        self.editor = UserF()
        self.viewer = UserF()

    def test_create(self):
        """Test create."""
        organisation = OrganisationF(
            name=self.name
        )
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
