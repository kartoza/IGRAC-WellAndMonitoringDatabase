from django import forms


class ReferenceElevationForm(forms.Form):
    """
    Form of reference elevation
    """
    value = forms.CharField(
        label='Value', required=False)
    unit = forms.CharField(
        label='Unit', required=False)
    description = forms.CharField(
        label='Description', required=False)
