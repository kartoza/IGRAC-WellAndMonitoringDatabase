from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.hydrogeology import PumpingTest


class PumpingTestForm(forms.ModelForm):
    """
    Form for PumpingTest.
    """

    class Meta:
        model = PumpingTest
        fields = ('porosity', 'hydraulic_conductivity', 'transmissivity', 'specific_storage',
                  'storativity', 'specific_capacity', 'test_type')
        widgets = {
            'hydraulic_conductivity': QuantityInput(unit_choices=['m', 'km']),
            'transmissivity': QuantityInput(unit_choices=['m2/day']),
            'specific_storage': QuantityInput(unit_choices=['%']),
            'specific_capacity': QuantityInput(unit_choices=['m2/day'])
        }

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
        return PumpingTestForm(initial=data)
