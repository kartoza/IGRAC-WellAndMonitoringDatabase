from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.reference_elevation import ReferenceElevation


class ReferenceElevationForm(forms.ModelForm):
    """
    Form of ReferenceElevation of well.
    """
    id = forms.CharField(required=False)

    class Meta:
        model = ReferenceElevation
        fields = ('value', 'description')
        widgets = {
            'value': QuantityInput(unit_group='length')
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: ReferenceElevation object
        :type instance: ReferenceElevation

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: ReferenceElevationForm
        """

        return ReferenceElevationForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: ReferenceElevation object
        :type instance: ReferenceElevation

        :return: Form
        :rtype: ReferenceElevationForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return ReferenceElevationForm(initial=data)
