from django import forms
from gwml2.models.well_construction.casing_component import (
    CasingMaterialTerm, CasingCoatingTerm, CasingFormTerm)


class WaterStrikeForm(forms.Form):
    """
    Form of water strike of well.
    """
    depth = forms.FloatField(required=False)
    description = forms.CharField(required=False)
