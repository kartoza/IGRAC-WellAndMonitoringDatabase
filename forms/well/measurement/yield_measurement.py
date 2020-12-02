from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.measurement.base import BaseMeasurementForm
from gwml2.models.well import WellYieldMeasurement


class WellYieldMeasurementForm(BaseMeasurementForm):
    """
    Form of WellYieldMeasurement of well.
    """

    class Meta:
        model = WellYieldMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value', 'info')
        widgets = {
            'value': QuantityInput(unit_required=False)
        }

    parameter_group = 'Yield Measurement'
