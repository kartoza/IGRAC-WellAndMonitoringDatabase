from gwml2.forms import (
    WellMetadataForm
)
from gwml2.utilities import get_organisations_as_editor
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class WellMetadataGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get_form(self, user):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            'well_metadata': WellMetadataForm.make_from_instance(
                self.well,
                organisation=get_organisations_as_editor(user))
        }


class WellMetadataCreateForm(FormGroupCreate):
    """ Collection form for general information section """

    def create(self):
        """ create form from data
        """
        if 'well_metadata' in self.data:
            self.form = self._make_form(
                self.well, WellMetadataForm,
                self.data['well_metadata']
            )

    def save(self):
        """ save all available data """
        if self.form:
            self.form.save()
