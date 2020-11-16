from gwml2.forms import (
    DrillingForm, WaterStrikeForm, StratigraphicLogForm, ReferenceElevationForm
)
from gwml2.models.drilling import (
    Drilling, StratigraphicLog, WaterStrike
)
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class DrillingGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            # drilling
            'drilling': DrillingForm.make_from_instance(
                self.well.drilling),
            'water_strike': WaterStrikeForm(),
            'stratigraphic_log': StratigraphicLogForm(),
        }


class DrillingCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    stratigraphic_log = []
    water_strike = []

    def create(self):
        """ create form from data
        """
        self.stratigraphic_log = []
        self.water_strike = []

        if self.data.get('drilling', None):
            self.form = self._make_form(
                self.well.drilling if self.well.drilling else Drilling(),
                DrillingForm, self.data['drilling'])

            if self.data['drilling'].get('stratigraphic_log', None):
                for log in self.data['drilling']['stratigraphic_log']:
                    obj = StratigraphicLog.objects.get(
                        id=log['id']) if log['id'] else StratigraphicLog()

                    self.stratigraphic_log.append(
                        self._make_form(
                            obj, StratigraphicLogForm, log))
            if self.data['drilling'].get('water_strike'):
                for water_strike in self.data['drilling']['water_strike']:
                    obj = WaterStrike.objects.get(
                        id=water_strike['id']) if water_strike['id'] else WaterStrike()

                    self.water_strike.append(
                        self._make_form(
                            obj, WaterStrikeForm, water_strike))

    def save(self):
        """ save all available data """
        if self.form:
            self.form.save()
            for water_strike in self.water_strike:
                water_strike.instance.drilling = self.form.instance
                water_strike.save()
            for log in self.stratigraphic_log:
                log.instance.drilling = self.form.instance
                log.save()
            self.well.drilling = self.form.instance
