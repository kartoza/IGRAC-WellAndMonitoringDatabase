from django import forms
from gwml2.models.well_management.organisation import Organisation


class CsvWellForm(forms.Form):
    """
    Form to upload CSV file.
    """
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        label='Organisation',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gw_well_file = forms.FileField(
        label="Well Descriptors:",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=True
    )
