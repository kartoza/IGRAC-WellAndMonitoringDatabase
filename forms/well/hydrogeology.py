import copy
from django import forms
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.hydrogeology import HydrogeologyParameter


class HydrogeologyParameterForm(forms.ModelForm):
    """
    Form for HydrogeologyParameter.
    """

    thickness_val = forms.CharField(required=False, label='thickness')

    class Meta:
        model = HydrogeologyParameter
        fields = ('aquifer_name', 'aquifer_material', 'aquifer_type', 'thickness', 'thickness_val', 'confinement')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: HydrogeologyParameter object
        :type instance: HydrogeologyParameter

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: HydrogeologyParameterForm
        """

        if data['thickness_val']:
            quantity, created = Quantity.objects.get_or_create(
                value=data['thickness_val'], unit='meters')
            data['thickness'] = quantity.id
        return HydrogeologyParameterForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: HydrogeologyParameter object
        :type instance: HydrogeologyParameter

        :return: Form
        :rtype: HydrogeologyParameterForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
            data['thickness_val'] = instance.thickness.value
        return HydrogeologyParameterForm(initial=data)
