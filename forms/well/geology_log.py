from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.geology import GeologyLog


class GeologyLogForm(forms.ModelForm):
    """
    Form of geology log of well.
    """
    id_ = forms.CharField(required=False)

    class Meta:
        model = GeologyLog
        fields = ('id_', 'top_depth', 'bottom_depth', 'material', 'geological_unit')
        widgets = {
            'top_depth': QuantityInput(unit_group='length'),
            'bottom_depth': QuantityInput(unit_group='length'),
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: GeologyLog object
        :type instance: GeologyLog

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeologyLogForm
        """

        return GeologyLogForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: GeologyLog object
        :type instance: GeologyLog

        :return: Form
        :rtype: GeologyLogForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        return GeologyLogForm(initial=data)
