from django import forms
from django.utils.translation import gettext_lazy as _
from gwml2.models.well_management.organisation import Organisation

class CsvWellForm(forms.Form):
    """
    Form to upload CSV file.
    """
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.filter(active=True).order_by('name'),
        label='Organisation',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gw_well_file = forms.FileField(
        label=_("General information"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False,
    )

    gw_well_monitoring_file = forms.FileField(
        label=_("Monitoring data"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False
    )

    gw_well_drilling_and_construction_file = forms.FileField(
        label=_("Drilling and donstruction data"),
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'accept': '.ods'}
        ),
        required=False
    )

    is_adding = forms.BooleanField(
        label=_(
            "The form will be processed for new wells."
        ),
        initial=True,
        required=False,
    )
    is_updating = forms.BooleanField(
        label=_(
            "The form will be used to update existing wells."
        ),
        initial=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['organisation'].empty_label = None
        self.fields['organisation'].required = True
        self.fields['organisation'].widget.attrs['required'] = True
