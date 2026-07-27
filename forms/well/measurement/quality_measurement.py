from django import forms
from django.forms.models import model_to_dict

from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.measurement.base import BaseMeasurementForm
from gwml2.models.well import WellQualityMeasurement


class WellQualityMeasurementForm(BaseMeasurementForm):
    """
    Form of WellQualityMeasurement of well.
    """
    depth = forms.Field(
        required=False,
        widget=QuantityInput(
            unit_group='length',
            unit_required=True,
            attrs={'id': 'measurement_depth'},
            quantity_saved=False
        ),
    )

    class Meta:
        model = WellQualityMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value')
        widgets = {
            'value': QuantityInput()
        }

    field_order = (
        'id', 'time', 'parameter', 'methodology', 'value', 'depth'
    )
    parameter_group = 'Quality Measurement'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['depth']:
            depth = self.cleaned_data['depth']
            instance.depth_value = depth.value
            instance.depth_unit = depth.unit
        if commit:
            instance.save()
        return instance

    @staticmethod
    def get_data_from_instance(instance):
        """ Create form from instance
        :return: dict
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        data['time'] = instance.time.strftime('%Y-%m-%d %H:%M:%S')
        data['depth'] = instance.depth
        return data

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :return: Form
        :rtype: WellQualityMeasurementForm
        """
        return WellQualityMeasurementForm(
            initial=WellQualityMeasurementForm.get_data_from_instance(
                instance), instance=instance)
