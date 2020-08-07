from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.drilling_and_construction import WaterStrike


class WaterStrikeForm(forms.ModelForm):
    """
    Form for WaterStrike.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = WaterStrike
        fields = ('id_', 'depth', 'description')
        widgets = {
            'depth': QuantityInput(unit_choices=['m', 'km'])
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WaterStrike object
        :type instance: WaterStrike

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WaterStrikeForm
        """
        return WaterStrikeForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WaterStrike object
        :type instance: WaterStrike

        :return: Form
        :rtype: WaterStrikeForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return WaterStrikeForm(initial=data)
