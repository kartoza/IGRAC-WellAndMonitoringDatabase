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
        return {
            'quality_measurement': WellQualityMeasurementForm(),  # manytomany form
        }


class QualityMeasurementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    measurements = []

    def create(self):
        """ create form from data
        """
        self.measurements = []
        for measurement in self.data['quality_measurement']['measurements']:
            if not measurement['time']:
                return
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
