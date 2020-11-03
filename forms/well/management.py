from django import forms
from django.forms.models import model_to_dict
from gwml2.models.management import Management
from gwml2.models.well_management.organisation import Organisation


class ManagementForm(forms.ModelForm):
    """
    Form for management.
    """
    organisation = forms.ModelChoiceField(
        queryset=None,
        label='Organisation',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Management
        fields = ('organisation', 'manager', 'description', 'groundwater_use', 'number_of_users')

    def __init__(self, *args, **kwargs):
        organisation = kwargs.get('organisation', None)
        if organisation:
            del kwargs['organisation']
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['organisation'].queryset = organisation

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

        return ManagementForm(
            data, files, instance=instance, organisation=Organisation.objects.all())

    @staticmethod
    def make_from_instance(instance, organisation):
        """ Create form from instance
        :param instance: Management object
        :type instance: Management

        :return: Form
        :rtype: ManagementForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
            data['organisation'] = instance.well.organisation
        return ManagementForm(initial=data, organisation=organisation)
