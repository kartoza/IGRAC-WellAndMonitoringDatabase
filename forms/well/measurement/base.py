from datetime import datetime

from django import forms
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup, TermMeasurementParameter
)
from gwml2.models.well import WellLevelMeasurement


class BaseMeasurementForm(WellBaseForm):
    """
    Form of Base Measurement of well.
    """
    id = forms.CharField(required=False)
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
        model = WellLevelMeasurement
        fields = (
            'id', 'time', 'parameter', 'methodology', 'value'
        )
        widgets = {
            'value': QuantityInput(unit_required=False),
        }

    field_order = (
        'id', 'time', 'parameter', 'methodology', 'value', 'depth'
    )
    parameter_group = None

    def __init__(self, *args, **kwargs):
        super(BaseMeasurementForm, self).__init__(*args, **kwargs)
        try:
            self.fields['parameter'].queryset = (
                TermMeasurementParameterGroup.objects.get(
                    name=self.parameter_group
                ).parameters.all()
            )
        except TermMeasurementParameterGroup.DoesNotExist:
            pass
        self.fields['time'].required = True
        self.fields['time'].widget.attrs['required'] = True
        self.fields['parameter'].empty_label = None
        self.fields['parameter'].required = True
        self.fields['parameter'].widget.attrs['required'] = True
        self.fields['time'].label = _('Date and Time')

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
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellLevelMeasurement object
        :type instance: WellLevelMeasurement

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: BaseMeasurementForm
        """
        if type(data['time']) == int:
            data['time'] = datetime.fromtimestamp(data['time'])

        # if parameter is string
        try:
            int(data['parameter'])
        except ValueError:
            try:
                data['parameter'] = TermMeasurementParameter.objects.get(
                    name=data['parameter']
                ).id
            except TermMeasurementParameter.DoesNotExist:
                pass

        return BaseMeasurementForm(data, files, instance=instance)

    @staticmethod
    def get_data_from_instance(instance):
        """ Create form from instance
        :return: Form
        :rtype: BaseMeasurementForm
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        data['time'] = instance.time.strftime('%Y-%m-%d %H:%M:%S')
        data['depth'] = instance.depth
        return data
