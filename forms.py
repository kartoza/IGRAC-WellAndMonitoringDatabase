from django import forms
from django.contrib.admin import widgets
from django.contrib.gis import forms as geoforms
from django.contrib.gis.forms.widgets import OSMWidget
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Submit,
    Field,
)
from gwml2.models.well.gw_well import GWWell
from gwml2.models.universal import Elevation


class CustomSelectMultipleWidget(widgets.FilteredSelectMultiple):

    class Media:
        css = {'all': ['/static/css/custom-widget.css',
                       '/static/css/jquery/ui/jquery-ui.min.css',
                       '/static/css/screen.css']}


class CsvWellForm(forms.Form):
    """Form to upload CSV file."""

    gw_location_file = forms.FileField(
        label="Choose GW Location Excel File:",
        widget=forms.FileInput(),
        required=False
    )

    gw_level_file = forms.FileField(
        label="Choose GW Level Excel File:",
        widget=forms.FileInput(),
        required=False
    )


class WellUpdateForm(forms.ModelForm):
    """Form for updating well."""

    gw_well_location = geoforms.PointField(widget=OSMWidget(
        attrs={
            'map_width': 750,
            'map_height': 400,
            'default_zoom': 5,
            'default_lat': -30.559482,
            'default_lon': 22.937506
        }), )
    gw_well_reference_elevation = forms.ModelMultipleChoiceField(
        queryset=Elevation.objects.all(),
        widget=CustomSelectMultipleWidget("elevation", is_stacked=False),
        required=False,
        help_text=_(
            'Reference elevation for all observations at the site, '
            'e.g. ground elevation, casing elevation.')
    )

    class Meta:
        model = GWWell
        fields = [
            'gw_well_name',
            'gw_well_location',
            'gw_well_reference_elevation',
            'gw_well_contribution_zone',
            'gw_well_unit',
            'gw_well_body',
            'gw_well_water_use',
            'gw_well_construction',
            'gw_well_total_length',
            'gw_well_status',
            'gw_well_static_water_depth',
            'gw_well_licence',
            'gw_well_constructed_depth',
            'gw_well_yield',
        ]

    def __init__(self, *args, **kwargs):
        form_title = 'Update Well'
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                Field('gw_well_name', css_class='form-control'),
                Field('gw_well_location', css_class='form-control'),
                Field('gw_well_reference_elevation', css_class='form-control'),
                Field('gw_well_contribution_zone', css_class='form-control'),
                Field('gw_well_unit', css_class='form-control'),
                Field('gw_well_body', css_class='form-control'),
                Field('gw_well_water_use', css_class='form-control'),
                Field('gw_well_construction', css_class='form-control'),
                Field('gw_well_total_length', css_class='form-control'),
                Field('gw_well_status', css_class='form-control'),
                Field('gw_well_static_water_depth', css_class='form-control'),
                Field('gw_well_licence', css_class='form-control'),
                Field('gw_well_constructed_depth', css_class='form-control'),
                Field('gw_well_yield', css_class='form-control'),
            )
        )

        self.helper.layout = layout
        self.helper.html5_required = False
        super(WellUpdateForm, self).__init__(*args, **kwargs)
