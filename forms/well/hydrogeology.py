from django import forms
from gwml2.models.hydrogeological_unit.gw_aquifer import AquiferTypeTerm


class HydrogeologyForm(forms.Form):
    """
    Form of hydro geology of well and spring
    """
    # Aquifer
    aquifer_name = forms.CharField()
    aquifer_material = forms.CharField()

    # Springs only
    average_yield = forms.FloatField()

    # wells only
    aquifer_type = forms.ModelChoiceField(
        queryset=AquiferTypeTerm.objects.all(),
        empty_label='------')
    specific_capacity = forms.FloatField()
    transmissivity = forms.FloatField()
    aquifer_thickness = forms.FloatField()
    specific_yield = forms.FloatField()
    storativity = forms.FloatField()
