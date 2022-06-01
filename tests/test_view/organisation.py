"""Test for Organisation View."""
from django.test import Client
from django.urls import reverse

from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF, UserF


class OrganisationViewTest(GWML2Test):
    """Test for Organisation View."""

    def setUp(self):
        """To setup test."""

        self.staff_password = 'staff'
        self.staff = UserF(
            password=self.staff_password,
            is_superuser=True
        )

        # For organisation 1
        self.admin_password = 'admin'
        self.admin = UserF(
            password=self.admin_password
        )
        self.editor_password = 'editor'
        self.editor = UserF(
            password=self.editor_password
        )
        self.viewer_password = 'viewer'
        self.viewer = UserF(
            password=self.viewer_password
        )
        self.organisation_1 = OrganisationF(
            admins=[self.admin.id],
            editors=[self.editor.id]
        )
        self.url_organisation_1 = reverse(
            'organisation_form', kwargs={
                'pk': self.organisation_1.pk
            }
        )

        # For organisation 1
        self.admin_2 = UserF(
            password=self.admin_password
        )
        self.editor_2 = UserF(
            password=self.editor_password
        )
        self.organisation_2 = OrganisationF(
            admins=[self.admin_2.id],
            editors=[self.editor_2.id]
        )
        self.url_organisation_2 = reverse(
            'organisation_form', kwargs={
                'pk': self.organisation_2.pk
            }
        )

        self.client = Client()

    def test_organisation_form_view_non_login(self):
        """Test accessing form with as non login.

        Should not be able to access all forms.
        """
        client = self.client
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 302)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 302)

    def test_organisation_form_view_staff(self):
        """Test accessing form with as staff.

        Should be able to access all forms.
        """
        client = self.client
        client.login(
            username=self.staff.username, password=self.staff_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 200)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 200)

    def test_organisation_form_view_admin_1(self):
        """Test accessing form with as admin_1.

        Should be able to access just organisation 1.
        """
        client = self.client
        client.login(
            username=self.admin.username, password=self.admin_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 200)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 401)

    def test_organisation_form_view_admin_2(self):
        """Test accessing form with as admin_2.

        Should be able to access just organisation 2.
        """
        client = self.client
        client.login(
            username=self.admin_2.username, password=self.admin_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 401)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 200)

    def test_organisation_form_view_editors(self):
        """Test accessing form with as editors.

        Should not be able to access all forms.
        """
        client = self.client
        client.login(
            username=self.editor.username, password=self.editor_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 401)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 401)

        client.login(
            username=self.editor_2.username, password=self.editor_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 401)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 401)

    def test_organisation_form_view_viewer(self):
        """Test accessing form with as viewer.

        Should not be able to access all forms.
        """
        client = self.client
        client.login(
            username=self.viewer.username, password=self.viewer_password)
        response = client.get(self.url_organisation_1)
        self.assertEquals(response.status_code, 401)
        response = client.get(self.url_organisation_2)
        self.assertEquals(response.status_code, 401)
