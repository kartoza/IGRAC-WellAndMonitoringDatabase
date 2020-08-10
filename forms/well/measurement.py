from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.well import WellMeasurement


class MeasurementForm(forms.ModelForm):
    """
    Form of measurement of well.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = WellMeasurement
        fields = ('id_', 'time', 'parameter', 'methodology', 'quality')
        widgets = {
            'quality': QuantityInput(unit_group='length')
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellMeasurement object
        :type instance: WellMeasurement

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WellMeasurementForm
        """

        return MeasurementForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellMeasurement object
        :type instance: WellMeasurement

        :return: Form
        :rtype: WellMeasurementForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return MeasurementForm(initial=data)
