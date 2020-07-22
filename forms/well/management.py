from django import forms


class ManagementForm(forms.Form):
    """Form for management."""
    groundwater_use = forms.CharField(required=False)
    number_of_people_served = forms.IntegerField(required=False)
