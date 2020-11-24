from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.hydrogeology import HydrogeologyParameter


class HydrogeologyParameterForm(WellBaseForm):
    """
    Form for HydrogeologyParameter.
    """

    class Meta:
        model = HydrogeologyParameter
        fields = ('aquifer_name', 'aquifer_material', 'aquifer_type', 'aquifer_thickness', 'confinement', 'degree_of_confinement')
        widgets = {
            'aquifer_thickness': QuantityInput(unit_group='length')
        }

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: HydrogeologyParameter object
        :type instance: HydrogeologyParameter

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: HydrogeologyParameterForm
        """

        return HydrogeologyParameterForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: HydrogeologyParameter object
        :type instance: HydrogeologyParameter

        :return: Form
        :rtype: HydrogeologyParameterForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return HydrogeologyParameterForm(initial=data, instance=instance)
