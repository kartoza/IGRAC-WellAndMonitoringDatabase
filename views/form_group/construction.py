from gwml2.forms import (
    ConstructionForm, CasingForm, ScreenForm, ReferenceElevationForm
)
from gwml2.models.construction import (
    Construction, Casing, Screen
)
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class ConstructionGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        casings = []
        screens = []
        if self.well.construction:
            for obj in self.well.construction.casing_set.all():
                casings.append(CasingForm.make_from_instance(obj))
            for obj in self.well.construction.screen_set.all():
                screens.append(ScreenForm.make_from_instance(obj))
        return {
            'construction': ConstructionForm.make_from_instance(
                self.well.construction),
            'casing': CasingForm(),
            'casings': casings,
            'screen': ScreenForm(),
            'screens': screens
        }


class ConstructionCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    casings = []
    screens = []

    def create(self):
        """ create form from data
        """
        self.casings = []
        self.screens = []

        self.form = self._make_form(
            self.well.construction if self.well.construction else Construction(),
            ConstructionForm, self.data['construction'])

        for casing in self.data['construction']['casing']:
            obj = Casing.objects.get(
                id=casing['id_']) if casing['id_'] else Casing()

            self.casings.append(
                self._make_form(
                    obj, CasingForm, casing
                )
            )
        for screen in self.data['construction']['screen']:
            obj = Screen.objects.get(
                id=screen['id_']) if screen['id_'] else Screen()

            self.screens.append(
                self._make_form(
                    obj, ScreenForm, screen
                )
            )

    def save(self):
        """ save all available data """
        self.form.save()
        for casing in self.casings:
            casing.instance.construction = self.form.instance
            casing.save()
        for screen in self.screens:
            screen.instance.construction = self.form.instance
            screen.save()
        self.well.construction = self.form.instance
