from django import forms
from django.forms.models import model_to_dict
from django.urls import reverse
from geonode.base.models import License, RestrictionCodeType
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.multi_value import MultiValueInput


class WellMetadataForm(WellBaseForm):
    """
    Form of metadata of well.
    """
    created_by = forms.CharField(required=False, disabled=True, label='Created by')
    created_at = forms.CharField(required=False, disabled=True, label='Created at')
    last_edited_by = forms.CharField(required=False, disabled=True, label='Last edited by')
    last_edited_at = forms.CharField(required=False, disabled=True, label='Last edited at')
    restriction_code_type = forms.ModelChoiceField(queryset=RestrictionCodeType.objects.all(), required=False)
    license = forms.ModelChoiceField(queryset=License.objects.all(), required=False)

    class Meta:
        model = Well
        fields = (
            'organisation', 'created_by', 'created_at', 'last_edited_by', 'last_edited_at', 'affiliate_organisations', 'public',
            'license', 'restriction_code_type', 'constraints_other')

    def __init__(self, *args, **kwargs):
        organisation = kwargs.get('organisation', None)
        try:
            del kwargs['organisation']
        except KeyError:
            pass
        super(WellMetadataForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].queryset = organisation
        self.fields['restriction_code_type'].label = 'Restrictions'
        self.fields['affiliate_organisations'].widget = MultiValueInput(
            url=reverse('organisation_autocomplete'), Model=Organisation, attrs={
                'placeholder': 'Please enter 1 or more character'
            }
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['license'] = cleaned_data['license'].id if cleaned_data['license'] else None
        cleaned_data['restriction_code_type'] = cleaned_data['restriction_code_type'].id if cleaned_data['restriction_code_type'] else None

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
