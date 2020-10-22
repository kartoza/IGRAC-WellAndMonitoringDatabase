from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.term_measurement_parameter import TermMeasurementParameterGroup
from gwml2.models.well import WellYieldMeasurement


class WellYieldMeasurementForm(forms.ModelForm):
    """
    Form of WellYieldMeasurement of well.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = WellYieldMeasurement
        fields = ('id_', 'time', 'parameter', 'methodology', 'value')
        widgets = {
            'value': QuantityInput(unit_required=False)
        }

    def __init__(self, *args, **kwargs):
        super(WellYieldMeasurementForm, self).__init__(*args, **kwargs)
        try:
            self.fields['parameter'].queryset = TermMeasurementParameterGroup.objects.get(
                name='Yield Measurement').parameters.all()
        except TermMeasurementParameterGroup.DoesNotExist:
            pass

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellWellYieldMeasurement object
        :type instance: WellWellYieldMeasurement

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WellWellYieldMeasurementForm
        """

        return WellYieldMeasurementForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellWellYieldMeasurement object
        :type instance: WellWellYieldMeasurement

        :return: Form
        :rtype: WellWellYieldMeasurementForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return WellYieldMeasurementForm(initial=data, instance=instance)
