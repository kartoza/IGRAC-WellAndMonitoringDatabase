from django import forms
from django.forms.models import model_to_dict
from gwml2.models.drilling_and_construction import DrillingAndConstruction


class DrillingAndConstructionForm(forms.ModelForm):
    """
    Form for DrillingAndConstructionForm.
    """

    class Meta:
        model = DrillingAndConstruction
        fields = ('drilling_method', 'driller', 'successful', 'pump_installer', 'pump_description')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Management object
        :type instance: Management

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: ManagementForm
        """

        return DrillingAndConstructionForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Management object
        :type instance: Management

        :return: Form
        :rtype: ManagementForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return DrillingAndConstructionForm(initial=data)
