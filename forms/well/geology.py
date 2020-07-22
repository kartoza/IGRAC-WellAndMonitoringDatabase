from django import forms


class GeologyForm(forms.Form):
    """
    Form of geology of well.
    """
    reference_elevation_value = forms.CharField(
        label='Value', required=False)
    reference_elevation_unit = forms.CharField(
        label='Unit', required=False)
    reference_elevation_description = forms.CharField(
        label='Description', required=False)
    total_depth = forms.FloatField()
