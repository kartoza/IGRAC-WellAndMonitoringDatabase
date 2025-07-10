from django import forms
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from geonode.base.models import License, RestrictionCodeType
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation


class WellMetadataForm(WellBaseForm):
    """
    Form of metadata of well.
    """
    created_by = forms.CharField(
        required=False, disabled=True, label=_('Created by'))
    created_at = forms.CharField(
        required=False, disabled=True, label=_('Created at'))
    last_edited_by = forms.CharField(
        required=False, disabled=True, label=_('Last edited by'))
    last_edited_at = forms.CharField(
        required=False, disabled=True, label=_('Last edited at'))

    # Organisation
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        required=True,
        label=_('Organisation')
    )
    license = forms.ModelChoiceField(
        disabled=True,
        queryset=License.objects.all(), required=False, label=_('License')
    )
    restriction_code_type = forms.ModelChoiceField(
        queryset=RestrictionCodeType.objects.all(),
        required=False,
        disabled=True,
        label=_('Restriction')
    )
    constraints_other = forms.CharField(
        label=_('Restriction code type'),
        required=False,
        widget=forms.TextInput(attrs={'disabled': 'disabled'})
    )

    class Meta:
        model = Well
        fields = (
            'organisation', 'created_by', 'created_at',
            'last_edited_by', 'last_edited_at',
            'license', 'restriction_code_type', 'constraints_other')

    def __init__(self, *args, **kwargs):
        organisation = kwargs.get('organisation', None)
        try:
            del kwargs['organisation']
        except KeyError:
            pass
        super(WellMetadataForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].queryset = organisation

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            del cleaned_data['license']
        except KeyError:
            pass
        try:
            del cleaned_data['restriction_code_type']
        except KeyError:
            pass
        try:
            del cleaned_data['constraints_other']
        except KeyError:
            pass

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
        return WellMetadataForm(
            data, files,
            instance=instance,
            organisation=Organisation.objects.all()
        )

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
        data['created_at'] = instance.created_at.strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )
        data['last_edited_by'] = instance.last_edited_by_username()
        data['last_edited_at'] = instance.last_edited_at.strftime(
            '%Y-%m-%d %H:%M:%S %Z'
        )

        # For licenses, it is coming from the organization
        license = instance.get_license()
        data['license'] = license.license_id
        data['restriction_code_type'] = license.restriction_code_type_id
        data['constraints_other'] = license.constraints_other
        return WellMetadataForm(
            initial=data, organisation=organisation
        )
