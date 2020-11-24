from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.reference_elevation import ReferenceElevationInput
from gwml2.models.drilling import WaterStrike


class WaterStrikeForm(WellBaseForm):
    """
    Form for WaterStrike.
    """
    id = forms.CharField(required=False)

    class Meta:
        model = WaterStrike
        fields = ('id', 'depth', 'description')
        widgets = {
            'depth': ReferenceElevationInput(unit_group='length')
        }

    field_order = ('id', 'depth', 'description')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WaterStrike object
        :type instance: WaterStrike

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WaterStrikeForm
        """
        return WaterStrikeForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WaterStrike object
        :type instance: WaterStrike

        :return: Form
        :rtype: WaterStrikeForm
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        return WaterStrikeForm(initial=data, instance=instance)
