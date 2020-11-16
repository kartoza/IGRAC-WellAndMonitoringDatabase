from gwml2.forms import ManagementForm, LicenseForm
from gwml2.models.management import Management, License
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate
from gwml2.utilities import get_organisations_as_editor


class ManagementGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get_form(self, user):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            'management': ManagementForm.make_from_instance(
                self.well.management,
                organisation=get_organisations_as_editor(user)),
            'license': LicenseForm.make_from_instance(
                self.well.management.license if self.well.management else None),
        }


class ManagementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    license_form = None

    def create(self):
        """ create form from data
        """
        if self.data.get('management', None):
            self.form = self._make_form(
                self.well.management if self.well.management else Management(),
                ManagementForm, self.data['management'])
            if self.data['management'].get('license', None):
                self.license_form = self._make_form(
                    self.form.instance.license if self.form.instance.license else License(),
                    LicenseForm, self.data['management']['license']
                )

    def save(self):
        """ save all available data """
        if self.license_form:
            self.license_form.save()
        if self.form:
            if self.license_form:
                self.form.instance.license = self.license_form.instance
            self.form.save()
            self.well.management = self.form.instance

            # safe the organisation
            org = self.form.cleaned_data.get('organisation', None)
            if org:
                self.well.organisation = org
