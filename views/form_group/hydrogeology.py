from gwml2.forms import (
    HydrogeologyParameterForm, PumpingTestForm
)
from gwml2.models.hydrogeology import (
    HydrogeologyParameter, PumpingTest
)
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class HydrogeologyGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            'hydrogeology': HydrogeologyParameterForm.make_from_instance(
                self.well.hydrogeology_parameter),
            'pumping_test': PumpingTestForm.make_from_instance(
                self.well.hydrogeology_parameter.pumping_test
                if self.well.hydrogeology_parameter else None),
        }


class HydrogeologyCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    pumping_test_form = None

    def create(self):
        """ create form from data
        """
        self.form = self._make_form(
            self.well.hydrogeology_parameter if self.well.hydrogeology_parameter else HydrogeologyParameter()
            , HydrogeologyParameterForm, self.data['hydrogeology'])

        self.pumping_test_form = self._make_form(
            self.form.instance.pumping_test if self.form.instance.pumping_test else PumpingTest(),
            PumpingTestForm, self.data['hydrogeology']['pumping_test']
        )

    def save(self):
        """ save all available data """
        self.pumping_test_form.save()
        self.form.instance.pumping_test = self.pumping_test_form.instance
        self.form.save()
        self.well.hydrogeology_parameter = self.form.instance
