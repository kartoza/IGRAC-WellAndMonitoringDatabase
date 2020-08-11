from gwml2.forms import WellQualityMeasurementForm
from gwml2.models.well import WellQualityMeasurement
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class QualityMeasurementGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        measurements = []
        for measurement in self.well.wellqualitymeasurement_set.all():
            measurements.append(WellQualityMeasurementForm.make_from_instance(measurement))
        return {
            'quality_measurement': WellQualityMeasurementForm(),  # manytomany form
            'quality_measurements': measurements,  # manytomany data
        }


class QualityMeasurementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    form = None
    measurements = []

    def create(self):
        """ create form from data
        """

        for measurement in self.data['quality_measurement']['measurements']:
            obj = WellQualityMeasurement.objects.get(
                id=measurement['id_']) if measurement['id_'] else WellQualityMeasurement()

            self.measurements.append(
                self._make_form(
                    obj, WellQualityMeasurementForm, measurement
                )
            )

    def save(self):
        """ save all available data """
        for measurement in self.measurements:
            measurement.instance.well = self.well
            measurement.save()
