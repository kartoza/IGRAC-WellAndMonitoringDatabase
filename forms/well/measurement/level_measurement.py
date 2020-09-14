from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.well import WellGroundwaterLevelMeasurement


class WellGroundwaterLevelMeasurementForm(forms.ModelForm):
    """
    Form of WellGroundwaterLevelMeasurement of well.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = WellGroundwaterLevelMeasurement
        fields = ('id_', 'time', 'parameter', 'methodology', 'quality')
        widgets = {
            'quality': QuantityInput(unit_group='length')
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellWellGroundwaterLevelMeasurement object
        :type instance: WellWellGroundwaterLevelMeasurement

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WellWellGroundwaterLevelMeasurementForm
        """

        return WellGroundwaterLevelMeasurementForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellWellGroundwaterLevelMeasurement object
        :type instance: WellWellGroundwaterLevelMeasurement

        :return: Form
        :rtype: WellWellGroundwaterLevelMeasurementForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return WellGroundwaterLevelMeasurementForm(initial=data, instance=instance)
