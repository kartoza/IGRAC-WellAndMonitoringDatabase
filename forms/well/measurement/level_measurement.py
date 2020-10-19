from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.well import WellLevelMeasurement


class WellLevelMeasurementForm(forms.ModelForm):
    """
    Form of WellLevelMeasurement of well.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = WellLevelMeasurement
        fields = ('id_', 'time', 'parameter', 'methodology', 'value')
        widgets = {
            'value': QuantityInput(unit_group='length')
        }

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
        :rtype: WellLevelMeasurementForm
        """

        return WellLevelMeasurementForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellLevelMeasurement object
        :type instance: WellLevelMeasurement

        :return: Form
        :rtype: WellLevelMeasurementForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return WellLevelMeasurementForm(initial=data, instance=instance)
