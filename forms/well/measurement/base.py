from datetime import datetime
from django import forms
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup, TermMeasurementParameter)
from gwml2.models.well import WellLevelMeasurement


class BaseMeasurementForm(WellBaseForm):
    """
    Form of Base Measurement of well.
    """
    id = forms.CharField(required=False)
    info = forms.CharField(required=False, disabled=True, label='Info')

    class Meta:
        model = WellLevelMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value')
        widgets = {
            'value': QuantityInput(unit_required=False)
        }

    field_order = ('id', 'time', 'parameter', 'methodology', 'value', 'info')
    parameter_group = None

    def __init__(self, *args, **kwargs):
        super(BaseMeasurementForm, self).__init__(*args, **kwargs)
        try:
            self.fields['parameter'].queryset = TermMeasurementParameterGroup.objects.get(
                name=self.parameter_group).parameters.all()
        except TermMeasurementParameterGroup.DoesNotExist:
            pass
        self.fields['time'].required = True
        self.fields['time'].widget.attrs['required'] = True
        self.fields['parameter'].empty_label = None
        self.fields['parameter'].required = True
        self.fields['parameter'].widget.attrs['required'] = True
        self.fields['value'].widget.attrs['min'] = 0
        self.fields['value'].widget.attrs['data-min'] = 0
        self.fields['time'].label = _('Date and Time')

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
                data['parameter'] = TermMeasurementParameter.objects.get(name=data['parameter']).id
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
        data['info'] = '&#013;'.join([
            'Created by : {}'.format(instance.created_by_username()),
            'Created at : {}'.format(instance.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')),
            'Last Edited by : {}'.format(instance.last_edited_by_username()),
            'Last edited at : {}'.format(instance.last_edited_at.strftime('%Y-%m-%d %H:%M:%S %Z')),
        ])
        data['time'] = instance.time.strftime('%Y-%m-%d %H:%M:%S')
        return data
