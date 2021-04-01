from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from gwml2.models.well_management.organisation import Organisation
from gwml2.forms.widgets.multi_value import MultiValueInput


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
    public = forms.BooleanField(
        initial=True,
        required=False
    )
    downloadable = forms.BooleanField(
        initial=True,
        required=False
    )
    affiliate_organisations = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Organisation.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gw_well_file = forms.FileField(
        label=_("General information"),
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    gw_well_monitoring_file = forms.FileField(
        label=_("Monitoring data"),
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, organisation, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['organisation'].queryset = organisation
        self.fields['organisation'].empty_label = None
        self.fields['organisation'].required = True
        self.fields['organisation'].widget.attrs['required'] = True
        self.fields['affiliate_organisations'].widget = MultiValueInput(
            url=reverse('organisation_autocomplete'), Model=Organisation, attrs={
                'placeholder': 'Please enter 1 or more character'
            }
        )
