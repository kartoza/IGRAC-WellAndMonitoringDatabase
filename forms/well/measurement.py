from django import forms
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.well import WellMeasurement


class MeasurementForm(forms.ModelForm):
    """
    Form of measurement of well.
    """
    id_ = forms.CharField(required=False)
    quality_val = forms.CharField(required=False, label='quality')

    class Meta:
        model = WellMeasurement
        fields = ('id_', 'time', 'parameter', 'methodology', 'quality_val')

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

        if data['quality_val']:
            quantity, created = Quantity.objects.get_or_create(value=data['quality_val'], unit='')
            instance.quality = quantity
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
        data['quality_val'] = instance.quality.value if instance.quality else ''
        return MeasurementForm(initial=data)
