from gwml2.forms import GeologyForm
from gwml2.models.geology import Geology
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class GeologyGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            'geology': GeologyForm.make_from_instance(
                self.well.geology),
        }


class GeologyCreateForm(FormGroupCreate):
    """ Collection form for general information section """

    def create(self):
        """ create form from data
        """
        if self.data.get('geology', None):
            self.form = self._make_form(
                self.well.geology if self.well.geology else Geology(),
                GeologyForm,
                self.data['geology'])

    def save(self):
        """ save all available data """
        if self.form:
            self.form.save()
            self.well.geology = self.form.instance
