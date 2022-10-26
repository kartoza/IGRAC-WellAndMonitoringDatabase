from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from gwml2.models.download_request import DownloadRequest
from gwml2.models.general import Country
from gwml2.models.well_management.organisation import OrganisationType

User = get_user_model()


class DownloadRequestForm(forms.ModelForm):
    countries = forms.MultipleChoiceField(
        label='Select the countries whose data you want to download.'
    )
    organization_types = forms.MultipleChoiceField()

    class Meta:
        model = DownloadRequest
        fields = (
            'countries', 'first_name', 'last_name', 'organization',
            'organization_types', 'email', 'country', 'data_type'
        )

    def __init__(self, *args, **kwargs):
        super(DownloadRequestForm, self).__init__(*args, **kwargs)
        self.fields['countries'].choices = [('all', 'All Countries')] + [
            (country.id, country.name) for
            country in Country.objects.all() if
            country.name]

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
