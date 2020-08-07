from django import forms
from django.forms.models import model_to_dict
from gwml2.models.drilling_and_construction import WaterStrike
from gwml2.models.general import Quantity


class WaterStrikeForm(forms.ModelForm):
    """
    Form for WaterStrike.
    """
    id_ = forms.CharField(required=False)
    depth_val = forms.CharField(required=False)

    class Meta:
        model = WaterStrike
        fields = ('id_', 'depth_val', 'description')

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
        if data['depth_val']:
            quantity, created = Quantity.objects.get_or_create(
                value=data['depth_val'], unit='meters')
            instance.depth = quantity

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
        data['depth_val'] = instance.depth.value if instance.depth else None
        return WaterStrikeForm(initial=data)
