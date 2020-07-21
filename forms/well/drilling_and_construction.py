from django import forms
from gwml2.models.contact_information import CIResponsibleParty
from gwml2.models.well_construction.borehole import BoreholeDrillingMethodTerm


class DrillingAndConstructionForm(forms.Form):
    """
    Form of drilling and construction of well.
    """
    drilling_method = forms.ModelChoiceField(
        queryset=BoreholeDrillingMethodTerm.objects.all(),
        empty_label='------')
    driller = forms.ModelChoiceField(
        queryset=CIResponsibleParty.objects.all(),
        empty_label='------')
    successful = forms.BooleanField(required=False)
