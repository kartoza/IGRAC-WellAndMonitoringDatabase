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
            'value': QuantityInput(unit_required=False)
        }

    parameter_group = 'Quality Measurement'
