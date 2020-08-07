from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.geology import Geology


class GeologyForm(forms.ModelForm):
    """
    Form of geology of well.
    """

    class Meta:
        model = Geology
        fields = ('total_depth',)
        widgets = {
            'total_depth': QuantityInput(unit_choices=['m', 'km']),
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Geology object
        :type instance: Geology

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeologyForm
        """
        return GeologyForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Geology object
        :type instance: Geology

        :return: Form
        :rtype: GeologyForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return GeologyForm(initial=data)
