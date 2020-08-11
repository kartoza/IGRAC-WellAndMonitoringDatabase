from gwml2.forms import WellYieldMeasurementForm
from gwml2.models.well import WellYieldMeasurement
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class YieldMeasurementGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        measurements = []
        for measurement in self.well.wellyieldmeasurement_set.all():
            measurements.append(WellYieldMeasurementForm.make_from_instance(measurement))
        return {
            'yield_measurement': WellYieldMeasurementForm(),  # manytomany form
            'yield_measurements': measurements,  # manytomany data
        }


class YieldMeasurementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    form = None
    measurements = []

    def create(self):
        """ create form from data
        """

        for measurement in self.data['yield_measurement']['measurements']:
            obj = WellYieldMeasurement.objects.get(
                id=measurement['id_']) if measurement['id_'] else WellYieldMeasurement()

            self.measurements.append(
                self._make_form(
                    obj, WellYieldMeasurementForm, measurement
                )
            )

    def save(self):
        """ save all available data """
        for measurement in self.measurements:
            measurement.instance.well = self.well
            measurement.save()
