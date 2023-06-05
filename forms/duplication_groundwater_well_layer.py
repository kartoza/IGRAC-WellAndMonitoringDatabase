import xml.etree.ElementTree as ET

import requests
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from geoserver.support import build_url

from geonode.geoserver.helpers import gs_catalog
from geonode.layers.models import Dataset
from gwml2.forms.widgets.multi_value import MultiValueInput
from gwml2.models.download_request import WELL_AND_MONITORING_DATA, GGMN
from gwml2.models.well_management.organisation import Organisation

User = get_user_model()


# TODO:
#  All hardcoded need to be saved on the preferences

class DuplicationGroundwaterWellLayerForm(forms.Form):
    layer = None
    well_type = forms.ChoiceField(
        choices=(
            (WELL_AND_MONITORING_DATA, WELL_AND_MONITORING_DATA),
            (GGMN, GGMN)
        )
    )
    name = forms.CharField(help_text='The layer name that will be created.')
    organisations = forms.ModelMultipleChoiceField(
        Organisation.objects.all(),
        widget=FilteredSelectMultiple('organisations', False),
        help_text=(
            'Organisation that will used to filter the data. '
            'Type minimum 3 character to show the list of organisation.'
        )
    )

    def __init__(self, *args, **kwargs):
        super(DuplicationGroundwaterWellLayerForm, self).__init__(
            *args, **kwargs
        )
        # init widget
        self.fields['organisations'].widget = MultiValueInput(
            url=reverse('organisation_autocomplete'), Model=Organisation
        )

    def target_layer_name(self, name):
        """Return target layer name"""
        return name.replace(' ', '_')

    def clean_well_type(self):
        well_type = self.cleaned_data['well_type']
        self.layer = None
        target_layer = None
        if well_type == WELL_AND_MONITORING_DATA:
            target_layer = 'groundwater:Groundwater_Well'
        elif well_type == GGMN:
            target_layer = 'groundwater:Groundwater_Well_GGMN'

        # Check target layer on geoserver
        if target_layer:
            self.layer = gs_catalog.get_layer(target_layer)
        if not self.layer:
            raise forms.ValidationError(
                f'{target_layer} does not found. Please contact admin.'
            )
        self.layer = self.layer
        return well_type

    def clean_name(self):
        name = self.cleaned_data['name']
        layer = self.layer
        if layer:
            workspace = layer.resource.workspace.name
            target_layer_name = self.target_layer_name(name)
            layer_name = f'{workspace}:{target_layer_name}'
            layer = gs_catalog.get_layer(layer_name)
            if layer:
                raise forms.ValidationError(
                    f'Layer with this name is already exist'
                )
        else:
            raise forms.ValidationError(
                f'Can not proceed, layer does not found'
            )
        return name

    def clean_organisations(self):
        return self.cleaned_data['organisations']

    def run(self):
        """Run it for duplication data."""
        name = self.cleaned_data['name']
        target_layer_name = name.replace(' ', '_')

        # Fetch the xml
        layer = self.layer
        xml_url = layer.resource.href
        xml = requests.get(xml_url).content

        # Update xml to new data
        tree = ET.ElementTree(ET.fromstring(xml))
        tree.find('name').text = target_layer_name
        tree.find('nativeName').text = target_layer_name
        tree.find(
            'metadata/entry/virtualTable/name').text = target_layer_name
        tree.find('title').text = name
        organisations = [f'{organisation.pk}' for organisation in self.cleaned_data['organisations']]
        sql = (
                "select id, ggis_uid, original_id, name, feature_type,purpose, status,organisation, country, year_of_drilling, aquifer_name, aquifer_type,manager, detail, location, created_at, created_by, last_edited_at, last_edited_by "
                "from mv_well where organisation_id IN (" +
                f"{','.join(organisations)}" +
                ") order by created_at DESC"
        )
        tree.find('metadata/entry/virtualTable/sql').text = sql
        xml = ET.tostring(
            tree.getroot(), encoding='utf8', method='xml'
        )

        # Create url
        workspace = layer.resource.workspace.name
        store = layer.resource.store.name
        upload_url = build_url(
            gs_catalog.service_url,
            [
                "workspaces",
                workspace,
                "datastores",
                store,
                "featuretypes"
            ]
        )

        # POST data
        headers = {"content-type": "text/xml"}
        r = requests.post(
            upload_url,
            data=xml,
            auth=(gs_catalog.username, gs_catalog.password),
            headers=headers,
        )

        # Need to handle the response
        if r.status_code == 201:
            layer = gs_catalog.get_layer(f'{workspace}:{target_layer_name}')
            style = gs_catalog.get_style(
                'Groundwater_Well', workspace='groundwater'
            )
            if style:
                layer.default_style = style
                gs_catalog.save(layer)
            call_command('updatelayers', filter=target_layer_name)
            try:
                dataset = Dataset.objects.get(
                    workspace=workspace, store=store, name=target_layer_name
                )
                return f'/catalogue/#/dataset/{dataset.pk}'
            except Dataset.DoesNotExist:
                return '/catalogue/#/search/?f=dataset'
            return
        else:
            raise Exception(r.content)
