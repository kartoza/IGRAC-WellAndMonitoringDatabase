from typing import Any
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from django.utils.translation import ugettext_lazy as _

from gwml2.models.download_request import DownloadRequest
from gwml2.models.general import Country
from gwml2.models.well_management.organisation import (
    Organisation,
    OrganisationType
)

User = get_user_model()


class DownloadRequestForm(forms.ModelForm):
    radio_filter_type = forms.ChoiceField(
        label='Filter by',
        choices=[
            ('countries', 'Countries'),
            ('data_providers', 'Data Providers')
        ],
        widget=forms.RadioSelect,
        initial='countries'
    )
    countries = forms.MultipleChoiceField(
        label='Select the countries whose data you want to download.',
        required=False
    )
    organisations = forms.MultipleChoiceField(
        label='Select the data providers whose data you want to download.',
        required=False
    )
    organization_types = forms.MultipleChoiceField()

    class Meta:
        model = DownloadRequest
        fields = (
            'radio_filter_type', 'countries', 'organisations',
            'first_name', 'last_name', 'organization',
            'organization_types', 'email', 'country', 'data_type'
        )

    def __init__(self, *args, **kwargs):
        super(DownloadRequestForm, self).__init__(*args, **kwargs)

        # Get country that has well
        with connections[settings.GWML2_DATABASE_CONFIG].cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT country_id FROM well WHERE country_id IS NOT NULL;")
            country_ids = [row[0] for row in cursor.fetchall()]

        self.fields['countries'].choices = [('all', 'All Countries')] + [
            (country.id, country.name) for
            country in Country.objects.filter(id__in=country_ids) if
            country.name
        ]

        self.fields['organisations'].choices = [
            ('all', 'All Data Providers')
        ] + [
            (organisation.id, organisation.name) for
            organisation in Organisation.objects.filter(
                active=True).order_by('name')
        ]

        types = [_type.name for _type in OrganisationType.objects.all()]
        self.fields['organization_types'].choices = [
            (_type.name, _type.name)
            for _type in OrganisationType.objects.all()]
        self.fields['organization_types'].label = _('Type of organization')

        # From POST data
        try:
            for _type in self.data.getlist('organization_types'):
                if _type not in types:
                    self.fields['organization_types'].choices += [
                        (_type, _type)
                    ]
        except (AttributeError, KeyError):
            pass

        # From initial
        try:
            for _type in self.initial['organization_types']:
                if _type not in types:
                    self.fields['organization_types'].choices += [
                        (_type, _type)
                    ]
        except (AttributeError, KeyError, TypeError):
            pass

    def clean_organization_types(self):
        organisation_types = self.cleaned_data['organization_types']
        return ', '.join(organisation_types)

    def clean_countries(self):
        countries = self.cleaned_data['countries']
        if 'all' in countries:
            return Country.objects.all()
        else:
            return Country.objects.filter(id__in=countries)

    def clean_organisations(self):
        organisations = self.cleaned_data['organisations']
        if 'all' in organisations:
            return Organisation.objects.filter(active=True)
        else:
            return Organisation.objects.filter(
                id__in=organisations
            ).filter(active=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        field_name = cleaned_data.get('radio_filter_type', 'countries')
        if field_name == 'countries' and not cleaned_data.get('countries'):
            raise forms.ValidationError(
                {
                    'countries': (
                        'Please select at least one of the countries'
                    )
                }
            )
        if (
            field_name == 'data_providers' and
            not cleaned_data.get('organisations')
        ):
            raise forms.ValidationError(
                {
                    'organisations': (
                        'Please select at least one of the organisations'
                    )
                }
            )
        return cleaned_data
