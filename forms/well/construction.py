from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.construction import Construction


class ConstructionForm(WellBaseForm):
    """
    Form for Construction.
    """

    class Meta:
        model = Construction
        fields = ('pump_installer', 'pump_description')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Construction object
        :type instance: Construction

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: ConstructionForm
        """

        return ConstructionForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Construction object
        :type instance: Construction

        :return: Form
        :rtype: ConstructionForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return ConstructionForm(initial=data, instance=instance)
