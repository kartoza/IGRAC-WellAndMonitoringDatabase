"""Forms for handling well data download requests."""
from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gwml2.models.download_request import DownloadRequest
from gwml2.models.general import Country
from gwml2.models.well_management.organisation import (
    Organisation,
    OrganisationType
)

User = get_user_model()


class DownloadRequestBaseForm(forms.ModelForm):
    """Abstract base form for download requests."""
    organization_types = forms.MultipleChoiceField(required=False)

    class Meta:
        model = DownloadRequest
        fields = ()

    def default_init(self):
        """Default initialization of the form."""

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
        return ', '.join(self.cleaned_data['organization_types'])


class DownloadRequestForm(DownloadRequestBaseForm):
    radio_filter_type = forms.ChoiceField(
        label='Filter by',
        choices=[
            ('data_providers', 'Data Providers'),
            ('countries', 'Countries')
        ],
        widget=forms.RadioSelect,
        initial='data_providers'
    )

    class Meta:
        model = DownloadRequest
        fields = (
            'countries', 'organisations',
            'first_name', 'last_name', 'organization',
            'organization_types', 'email', 'country', 'data_type'
        )

    def __init__(self, *args, **kwargs):
        super(DownloadRequestForm, self).__init__(*args, **kwargs)

        self.fields['countries'].label = (
            'Select the countries whose data you want to download.'
        )
        self.fields['organisations'].label = (
            'Select the data providers whose data you want to download.'
        )
        self.default_init()

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


class DownloadRequestByIdsForm(DownloadRequestBaseForm):
    """Download request form for downloading data by ids."""

    wells_id = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = DownloadRequest
        fields = (
            'wells_id', 'first_name', 'last_name', 'organization',
            'organization_types', 'email', 'country', 'data_type'
        )

    def __init__(self, *args, **kwargs):
        super(DownloadRequestByIdsForm, self).__init__(*args, **kwargs)
        self.default_init()

    def clean_wells_id(self):
        raw = self.data.getlist('wells_id')
        try:
            ids = [int(i) for i in raw if i]
        except (ValueError, TypeError):
            raise forms.ValidationError('wells_id must be a list of integers.')
        if len(ids) < 1:
            raise forms.ValidationError('At least 1 well must be selected.')
        if len(ids) > 100000:
            raise forms.ValidationError(
                'Cannot request more than 100,000 wells at once.'
            )
        return ids
