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
