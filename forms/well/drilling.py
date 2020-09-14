from django import forms
from django.forms.models import model_to_dict
from gwml2.models.drilling import Drilling


class DrillingForm(forms.ModelForm):
    """
    Form for Drilling.
    """

    class Meta:
        model = Drilling
        fields = ('drilling_method', 'driller', 'successful', 'cause_of_failure')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Drilling object
        :type instance: Drilling

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: DrillingForm
        """

        return DrillingForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Drilling object
        :type instance: Drilling

        :return: Form
        :rtype: DrillingForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return DrillingForm(initial=data)
