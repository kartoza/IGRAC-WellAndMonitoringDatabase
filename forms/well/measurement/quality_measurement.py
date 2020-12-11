from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.measurement.base import BaseMeasurementForm
from gwml2.models.well import WellQualityMeasurement


class WellQualityMeasurementForm(BaseMeasurementForm):
    """
    Form of WellQualityMeasurement of well.
    """

    class Meta:
        model = WellQualityMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value','info')
        widgets = {
            'value': QuantityInput()
        }

    parameter_group = 'Quality Measurement'

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :return: Form
        :rtype: WellQualityMeasurementForm
        """
        return WellQualityMeasurementForm(
            initial=WellQualityMeasurementForm.get_data_from_instance(
                instance), instance=instance)
