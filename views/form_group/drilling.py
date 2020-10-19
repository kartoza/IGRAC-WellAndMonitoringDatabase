from gwml2.forms import (
    DrillingForm, WaterStrikeForm, StratigraphicLogForm, ReferenceElevationForm
)
from gwml2.models.drilling import (
    Drilling, StratigraphicLog, WaterStrike
)
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class DrillingGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        water_strikes = []
        stratigraphic_logs = []
        if self.well.drilling:
            for obj in self.well.drilling.waterstrike_set.all():
                water_strikes.append(WaterStrikeForm.make_from_instance(obj))
            for obj in self.well.drilling.stratigraphiclog_set.all():
                stratigraphic_logs.append(StratigraphicLogForm.make_from_instance(obj))
        return {
            # drilling
            'drilling': DrillingForm.make_from_instance(
                self.well.drilling),
            'water_strike': WaterStrikeForm(),
            'water_strikes': water_strikes,
            'stratigraphic_log': StratigraphicLogForm(),
            'stratigraphic_logs': stratigraphic_logs
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

        self.form = self._make_form(
            self.well.drilling if self.well.drilling else Drilling(),
            DrillingForm, self.data['drilling'])

        for log in self.data['drilling']['stratigraphic_log']:
            obj = StratigraphicLog.objects.get(
                id=log['id_']) if log['id_'] else StratigraphicLog()

            self.stratigraphic_log.append(
                self._make_form(
                    obj, StratigraphicLogForm, log))

        for water_strike in self.data['drilling']['water_strike']:
            obj = WaterStrike.objects.get(
                id=water_strike['id_']) if water_strike['id_'] else WaterStrike()

            self.water_strike.append(
                self._make_form(
                    obj, WaterStrikeForm, water_strike))

    def save(self):
        """ save all available data """
        self.form.save()
        for water_strike in self.water_strike:
            water_strike.instance.drilling = self.form.instance
            water_strike.save()
        for log in self.stratigraphic_log:
            log.instance.drilling = self.form.instance
            log.save()
        self.well.drilling = self.form.instance
