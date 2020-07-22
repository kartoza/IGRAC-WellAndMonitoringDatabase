from django import forms
from gwml2.models.well_construction.screen_component import (
    AttachmentMethodTerm, ScreenCoatingTerm, ScreenFormTerm, ScreenMaterialTerm,
    PerforationMethodTerm, ScreenFittingTerm, ScreenPlacementTerm)


class ScreenForm(forms.Form):
    """
    Form of screen well.
    """
    attachment_method = forms.ModelChoiceField(
        queryset=AttachmentMethodTerm.objects.all(), required=False)
    coating = forms.ModelChoiceField(
        queryset=ScreenCoatingTerm.objects.all(), required=False)
    form = forms.ModelChoiceField(
        queryset=ScreenFormTerm.objects.all(), required=False)
    material = forms.ModelChoiceField(
        queryset=ScreenMaterialTerm.objects.all(), required=False)
    perforation_method = forms.ModelChoiceField(
        queryset=PerforationMethodTerm.objects.all(), required=False)
    fitting = forms.ModelChoiceField(
        queryset=ScreenFittingTerm.objects.all(), required=False)
    placement = forms.ModelChoiceField(
        queryset=ScreenPlacementTerm.objects.all(), required=False)
    hole_size = forms.FloatField(required=False)
    internal_diameter = forms.FloatField(required=False)
    external_diameter = forms.FloatField(required=False)
    wall_thickness = forms.FloatField(required=False)
