from django import forms
from gwml2.models.well_construction.casing_component import (
    CasingMaterialTerm, CasingCoatingTerm, CasingFormTerm)


class CasingForm(forms.Form):
    """
    Form of casing of well.
    """
    material = forms.ModelChoiceField(
        queryset=CasingMaterialTerm.objects.all(), required=False)
    coating = forms.ModelChoiceField(
        queryset=CasingCoatingTerm.objects.all(), required=False)
    form = forms.ModelChoiceField(
        queryset=CasingFormTerm.objects.all(), required=False)
    internal_diameter = forms.FloatField(required=False)
    external_diameter = forms.FloatField(required=False)
    wall_thickness = forms.FloatField(required=False)
