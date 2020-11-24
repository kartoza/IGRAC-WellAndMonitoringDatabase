from django import forms
from django.forms.models import model_to_dict
from django.urls import reverse
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.multi_value.organisations import MultiOrganisationInput


class WellMetadataForm(WellBaseForm):
    """
    Form of metadata of well.
    """
    created_by = forms.CharField(required=False, disabled=True, label='Created by')
    created_at = forms.CharField(required=False, disabled=True, label='Created at')
    last_edited_by = forms.CharField(required=False, disabled=True, label='Last edited by')
    last_edited_at = forms.CharField(required=False, disabled=True, label='Last edited at')

    class Meta:
        model = Well
        fields = ('organisation', 'created_by', 'created_at', 'last_edited_by', 'last_edited_at', 'affiliate_organisations')

    def __init__(self, *args, **kwargs):
        organisation = kwargs.get('organisation', None)
        try:
            del kwargs['organisation']
        except KeyError:
            pass
        super(WellMetadataForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].queryset = organisation
        self.fields['affiliate_organisations'].widget = MultiOrganisationInput(url=reverse('organisation_autocomplete'))

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: well object
        :type instance: Well

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeneralInformationForm
        """
        return WellMetadataForm(data, files, instance=instance, organisation=Organisation.objects.all())

    @staticmethod
    def make_from_instance(instance, organisation):
        """ Create form from instance
        :param instance: well object
        :type instance: Well

        :return: Form
        :rtype: GeneralInformationForm
        """
        data = model_to_dict(instance)
        data['created_by'] = instance.created_by_username()
        data['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')
        data['last_edited_by'] = instance.last_edited_by_username()
        data['last_edited_at'] = instance.last_edited_at.strftime('%Y-%m-%d %H:%M:%S %Z')
        return WellMetadataForm(
            initial=data, organisation=organisation
        )
