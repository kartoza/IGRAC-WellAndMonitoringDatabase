from django import forms
from gwml2.models.general_information import CIResponsibleParty
from gwml2.models.well_construction.borehole import BoreholeDrillingMethodTerm


class DrillingAndConstructionForm(forms.Form):
    """
    Form of drilling and construction of well.
    """
    drilling_method = forms.ModelChoiceField(
        queryset=BoreholeDrillingMethodTerm.objects.all(),
        empty_label='------',
        help_text="Method of drilling.")
    driller = forms.ModelChoiceField(
        queryset=CIResponsibleParty.objects.all(),
        empty_label='------',
        help_text="The organisation responsible for drilling the "
                  "borehole (as opposed to commissioning the borehole).")
    successful = forms.BooleanField(required=False)

    # pump
    pump_installer = forms.CharField(required=False)
    pump_details = forms.CharField(required=False)
