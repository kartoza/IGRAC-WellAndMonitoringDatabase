from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.construction import Screen


class ScreenForm(forms.ModelForm):
    """
    Form for Screen.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = Screen
        fields = ('id_', 'top_depth', 'bottom_depth',
                  'diameter', 'material', 'description')
        widgets = {
            'top_depth': QuantityInput(unit_group='length'),
            'bottom_depth': QuantityInput(unit_group='length'),
            'diameter': QuantityInput(unit_group='length'),
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Screen object
        :type instance: Screen

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: ScreenForm
        """
        return ScreenForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Screen object
        :type instance: Screen

        :return: Form
        :rtype: ScreenForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return ScreenForm(initial=data)
