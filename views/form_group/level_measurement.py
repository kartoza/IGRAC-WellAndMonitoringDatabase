from gwml2.forms import WellLevelMeasurementForm
from gwml2.models.well import WellLevelMeasurement
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class LevelMeasurementGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        return {
            'level_measurement': WellLevelMeasurementForm(),  # manytomany form
        }


class LevelMeasurementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    well_level = None
    measurements = []

    def create(self):
        """ create form from data
        """
        self.measurements = []
        for measurement in self.data['level_measurement']['measurements']:
            if not measurement['time']:
                return
            obj = WellLevelMeasurement.objects.get(
                id=measurement['id_']) if measurement['id_'] else WellLevelMeasurement()

            self.measurements.append(
                self._make_form(
                    obj, WellLevelMeasurementForm, measurement
                )
            )

    def save(self):
        """ save all available data """
        for measurement in self.measurements:
            measurement.instance.well = self.well
            measurement.save()
