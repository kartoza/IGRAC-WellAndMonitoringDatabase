from django import forms


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
        label="Well Descriptors:",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    gw_well_monitoring_file = forms.FileField(
        label="Well Monitoring:",
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, organisation, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['organisation'].queryset = organisation
