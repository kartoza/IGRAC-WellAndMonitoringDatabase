from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.geology import Geology


class GeologyForm(WellBaseForm):
    """
    Form of geology of well.
    """

    class Meta:
        model = Geology
        fields = ('total_depth', 'reference_elevation')
        widgets = {
            'total_depth': QuantityInput(
                unit_group='length', attrs={
                    'min': 0
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(GeologyForm, self).__init__(*args, **kwargs)

    def clean_total_depth(self):
        value = self.cleaned_data.get('total_depth', None)
        if value and value.value < 0:
            raise forms.ValidationError('Should be positive')
        return value

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Geology object
        :type instance: Drilling

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeologyForm
        """
        if not data['total_depth_value']:
            data['reference_elevation'] = None
        return GeologyForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Geology object
        :type instance: Drilling

        :return: Form
        :rtype: GeologyForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return GeologyForm(initial=data)
