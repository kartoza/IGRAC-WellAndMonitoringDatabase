from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.measurement.base import BaseMeasurementForm
from gwml2.models.well import WellLevelMeasurement


class WellLevelMeasurementForm(BaseMeasurementForm):
    """
    Form of WellLevelMeasurement of well.
    """

    class Meta:
        model = WellLevelMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value', 'info')
        widgets = {
            'value': QuantityInput(unit_required=False)
        }

    parameter_group = 'Level Measurement'


    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :return: Form
        :rtype: WellLevelMeasurementForm
        """
        return WellLevelMeasurementForm(
            initial=WellLevelMeasurementForm.get_data_from_instance(
                instance), instance=instance)
