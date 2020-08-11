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
            'stratigraphic_logs': stratigraphic_logs,
            'drilling_elevation': ReferenceElevationForm.make_from_instance(
                self.well.drilling.reference_elevation
                if self.well.drilling else None),
        }


class DrillingCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    form = None
    elevation_form = None
    stratigraphic_log = []
    water_strike = []

    def create(self):
        """ create form from data
        """
        self.form = self._make_form(
            self.well.drilling if self.well.drilling else Drilling(),
            DrillingForm, self.data['drilling'])

        # reference elevation
        self.elevation_form = self._make_form(
            self.form.instance.reference_elevation \
                if self.form.instance.reference_elevation else ReferenceElevation(),
            ReferenceElevationForm, self.data['drilling']['reference_elevation'])

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

        self.elevation_form.save()
        self.form.instance.reference_elevation = self.elevation_form.instance
        self.form.save()
        for water_strike in self.water_strike:
            water_strike.instance.drilling = self.form.instance
            water_strike.save()
        for log in self.stratigraphic_log:
            log.instance.drilling = self.form.instance
            log.save()
        self.well.drilling = self.form.instance
