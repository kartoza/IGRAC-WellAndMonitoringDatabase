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
