from django import forms
from django.utils.translation import ugettext_lazy as _

from geonode.base.models import License, RestrictionCodeType


class CsvWellForm(forms.Form):
    """
    Form to upload CSV file.
    """
    organisation = forms.ModelChoiceField(
        queryset=None,
        label='Organisation',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gw_well_file = forms.FileField(
        label=_("General information"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False,
    )

    gw_well_monitoring_file = forms.FileField(
        label=_("Monitoring data"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False
    )

    gw_well_drilling_and_construction_file = forms.FileField(
        label=_("Drilling and donstruction data"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False
    )

    is_adding = forms.BooleanField(
        label=_(
            "The form will be processed for new wells."
        ),
        initial=True,
        required=False,
    )
    is_updating = forms.BooleanField(
        label=_(
            "The form will be used to update existing wells."
        ),
        initial=True,
        required=False,
    )

    # Licenses
    license = forms.ModelChoiceField(
        queryset=License.objects.all(), required=False, label=_('License'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    restriction_code_type = forms.ModelChoiceField(
        queryset=RestrictionCodeType.objects.all(),
        required=False, label=_('Restriction'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    constraints_other = forms.CharField(
        required=False,
        label=_('Restrictions other'),
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    def __init__(self, organisation, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['organisation'].queryset = organisation
        self.fields['organisation'].empty_label = None
        self.fields['organisation'].required = True
        self.fields['organisation'].widget.attrs['required'] = True

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['license'] = cleaned_data['license'].id if cleaned_data[
            'license'] else None
        cleaned_data['restriction_code_type'] = cleaned_data[
            'restriction_code_type'].id if cleaned_data[
            'restriction_code_type'] else None
