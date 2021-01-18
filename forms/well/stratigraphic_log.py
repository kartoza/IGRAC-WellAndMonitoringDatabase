from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.drilling import StratigraphicLog


class StratigraphicLogForm(WellBaseForm):
    """
    Form of geology log of well.
    """
    id = forms.CharField(required=False)

    class Meta:
        model = StratigraphicLog
        fields = ('id', 'reference_elevation', 'top_depth', 'bottom_depth', 'material', 'stratigraphic_unit')
        widgets = {
            'top_depth': QuantityInput(unit_group='length'),
            'bottom_depth': QuantityInput(unit_group='length'),
        }

    field_order = ('id', 'reference_elevation', 'top_depth', 'bottom_depth', 'material', 'stratigraphic_unit')

    def __init__(self, *args, **kwargs):
        super(StratigraphicLogForm, self).__init__(*args, **kwargs)
        self.fields['reference_elevation'].empty_label = None
        self.fields['reference_elevation'].required = True
        self.fields['reference_elevation'].widget.attrs['required'] = True

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: StratigraphicLog object
        :type instance: StratigraphicLog

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: StratigraphicLogForm
        """

        return StratigraphicLogForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: StratigraphicLog object
        :type instance: StratigraphicLog

        :return: Form
        :rtype: StratigraphicLogForm
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        return StratigraphicLogForm(initial=data, instance=instance)
