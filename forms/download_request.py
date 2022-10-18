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
    organisation_types = forms.MultipleChoiceField()

    class Meta:
        model = DownloadRequest
        fields = (
            'countries', 'name', 'surname', 'organisation',
            'position', 'organisation_types', 'email')

    def __init__(self, *args, **kwargs):
        super(DownloadRequestForm, self).__init__(*args, **kwargs)
        self.fields['countries'].choices = [('all', 'All Countries')] + [
            (country.id, country.name) for
            country in Country.objects.all() if
            country.name]
        self.fields['organisation_types'].choices = [
            (_type.name, _type.name)
            for _type in OrganisationType.objects.all()]
        self.fields['organisation_types'].label = _('Type of organization')

        try:
            if self.data['organisation_types']:
                self.fields['organisation_types'].choices += [
                    (
                        self.data['organisation_types'],
                        self.data['organisation_types']
                    )
                ]
        except KeyError:
            pass

    def clean_organisation_types(self):
        organisation_types = self.cleaned_data['organisation_types']
        return ', '.join(organisation_types)

    def clean_countries(self):
        countries = self.cleaned_data['countries']
        if 'all' in countries:
            return Country.objects.all()
        else:
            return Country.objects.filter(id__in=countries)
