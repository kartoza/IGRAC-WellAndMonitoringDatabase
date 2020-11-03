from gwml2.forms import ManagementForm, LicenseForm
from gwml2.models.management import Management, License
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate
from gwml2.utilities import get_organisations


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
                organisation=get_organisations(user)),
            'license': LicenseForm.make_from_instance(
                self.well.management.license if self.well.management else None),
        }


class ManagementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    license_form = None

    def create(self):
        """ create form from data
        """
        self.form = self._make_form(
            self.well.management if self.well.management else Management(),
            ManagementForm, self.data['management'])
        self.license_form = self._make_form(
            self.form.instance.license if self.form.instance.license else License(),
            LicenseForm, self.data['management']['license']
        )

    def save(self):
        """ save all available data """
        self.license_form.save()
        self.form.instance.license = self.license_form.instance
        self.form.save()
        self.well.management = self.form.instance
        org = self.form.cleaned_data.get('organisation', None)
        if org:
            self.well.organisation = org
