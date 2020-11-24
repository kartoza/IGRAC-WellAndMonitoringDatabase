from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.management import License


class LicenseForm(WellBaseForm):
    """
    Form for License.
    """

    class Meta:
        model = License
        fields = ('number', 'valid_from', 'valid_until', 'description')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: License object
        :type instance: License

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: LicenseForm
        """

        return LicenseForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: License object
        :type instance: License

        :return: Form
        :rtype: LicenseForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return LicenseForm(initial=data)
