import copy
from django import forms
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.hydrogeology import PumpingTest


class PumpingTestForm(forms.ModelForm):
    """
    Form for PumpingTest.
    """
    hydraulic_conductivity_val = forms.CharField(
        required=False, label='hydraulic conductivity')
    transmissivity_val = forms.CharField(
        required=False, label='transmissivity')
    specific_storage_val = forms.CharField(
        required=False, label='specific storage')
    specific_capacity_val = forms.CharField(
        required=False, label='specific capacity')

    class Meta:
        model = PumpingTest
        fields = ('porosity', 'hydraulic_conductivity', 'hydraulic_conductivity_val', 'transmissivity',
                  'transmissivity_val', 'specific_storage', 'specific_storage_val',
                  'storativity', 'specific_capacity', 'specific_capacity_val', 'test_type')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: PumpingTest object
        :type instance: PumpingTest

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: PumpingTestForm
        """

        if data['hydraulic_conductivity_val']:
            quantity, created = Quantity.objects.get_or_create(value=data['hydraulic_conductivity_val'])
            data['hydraulic_conductivity'] = quantity.id
        if data['transmissivity_val']:
            quantity, created = Quantity.objects.get_or_create(value=data['transmissivity_val'], unit='m2/day')
            data['transmissivity'] = quantity.id
        if data['specific_storage_val']:
            quantity, created = Quantity.objects.get_or_create(value=data['specific_storage_val'], unit='%')
            data['specific_storage'] = quantity.id
        if data['specific_capacity_val']:
            quantity, created = Quantity.objects.get_or_create(value=data['specific_capacity_val'], unit='m2/day')
            data['specific_capacity'] = quantity.id
        return PumpingTestForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: PumpingTest object
        :type instance: PumpingTest

        :return: Form
        :rtype: PumpingTestForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
            data['hydraulic_conductivity_val'] = instance.hydraulic_conductivity.value
            data['transmissivity_val'] = instance.transmissivity.value
            data['specific_storage_val'] = instance.specific_storage.value
            data['specific_capacity_val'] = instance.specific_capacity.value
        return PumpingTestForm(initial=data)
