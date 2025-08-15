import json
import os
import zipfile
from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Country
from gwml2.models.well_management.organisation import (
    Organisation, OrganisationGroup
)
from gwml2.serializer.organisation_contributor import (
    OrganisationContributorSerializer
)
from igrac.models import SitePreference

WELL_AND_MONITORING_DATA = 'Well and Monitoring Data'
GGMN = 'GGMN'
DEFAULT_README_HEADER_TEXT = (
    "=======================================================\r\n"
    "IGRAC Groundwater Monitoring Data - README\r\n"
    "======================================================="
)


class DownloadRequest(models.Model):
    """Request data to download the well data."""

    uuid = models.UUIDField(
        default=uuid4,
        editable=False
    )
    request_at = models.DateTimeField(
        _('Requested at'),
        default=datetime.now, blank=True
    )
    data_type = models.CharField(
        _('Data type'),
        default=GGMN,
        choices=(
            (GGMN, GGMN),
            (WELL_AND_MONITORING_DATA, 'Groundwater Observations Repository'),
        ),
        max_length=512
    )
    user_id = models.IntegerField(null=True, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    countries = models.ManyToManyField(
        Country,
        null=True, blank=True,
        related_name='download_country_data_request'
    )
    organisations = models.ManyToManyField(
        Organisation,
        null=True, blank=True,
        related_name='download_organisation_data_request'
    )
    first_name = models.CharField(
        _('First Name'), max_length=512
    )
    last_name = models.CharField(
        _('Last Name'), null=True, blank=True, max_length=512
    )
    organization = models.CharField(
        _('Organization'),
        max_length=512,
    )
    organization_types = models.CharField(
        _('Type of organization'),
        max_length=512,
    )
    country = models.ForeignKey(
        Country,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    is_ready = models.BooleanField(default=False)

    output_folder = os.path.join(settings.MEDIA_ROOT, 'request')

    organisations_found = []

    def generate_file(self):
        """Generate file to be downloaded."""
        self.organisations_found = []
        from gwml2.tasks.data_file_cache.country_recache import (
            COUNTRY_DATA_FOLDER
        )
        from gwml2.tasks.data_file_cache.organisation_cache import (
            ORGANISATION_DATA_FOLDER
        )
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        request_file = os.path.join(
            self.output_folder, '{}.zip'.format(str(self.uuid))
        )

        zip_file = zipfile.ZipFile(request_file, 'w')
        if self.countries.exists():
            self._write_countries_to_zip_file(COUNTRY_DATA_FOLDER, zip_file)
        elif self.organisations.exists():
            self._write_organisations_to_zip_file(
                ORGANISATION_DATA_FOLDER, zip_file
            )
        zip_file.writestr(
            'Readme.txt', self._generate_readme_file(COUNTRY_DATA_FOLDER)
        )
        zip_file.close()

        # Make this downloader done
        self.is_ready = True
        self.save()

    def _add_content_to_zip_file(
            self, data_folder, data_file_name, zip_file
    ) -> bool:
        data_file = os.path.join(data_folder, data_file_name)
        if os.path.exists(data_file):
            zip_file.write(
                data_file, data_file_name,
                compress_type=zipfile.ZIP_DEFLATED
            )
            return True
        return False

    def _write_countries_to_zip_file(self, data_folder, zip_file):
        for country in self.countries.all():
            data_file_name = f'{country.code} - {self.data_type}.zip'
            self._add_content_to_zip_file(
                data_folder, data_file_name, zip_file
            )

    def _write_organisations_to_zip_file(self, data_folder, zip_file):
        for organisation in self.organisations.all():
            data_file_name = f'{str(organisation.name)} - {self.data_type}.zip'
            added = self._add_content_to_zip_file(
                data_folder, data_file_name, zip_file
            )
            if added:
                self.organisations_found.append(organisation.name)

    def _get_readme_text(self):
        pref = SitePreference.objects.first()
        if pref is None:
            return DEFAULT_README_HEADER_TEXT
        if self.data_type == GGMN:
            ggmn_group = OrganisationGroup.get_ggmn_group()
            header_text = ggmn_group.download_readme_text
        else:
            header_text = pref.download_readme_text
        return header_text if header_text else DEFAULT_README_HEADER_TEXT

    def _get_organisations_in_countries(
            self, country: Country, country_data_folder
    ):
        """Return organisations of countries."""
        # This is new approach
        _organisation_file_name = (
            f'{country.code} - organisations.json'
        )
        _file_path = os.path.join(
            country_data_folder,
            _organisation_file_name
        )
        if os.path.exists(_file_path):
            with open(_file_path, "r") as _file:
                try:
                    data = json.loads(_file.read())
                    organisations = data[self.data_type]
                    return Organisation.objects.filter(id__in=organisations)
                except KeyError:
                    pass
        return None

    def _generate_readme_file(self, country_data_folder):
        """Generate readme."""
        header_text = self._get_readme_text()
        header_text += '\r\n'
        header_text += '\r\n'
        header_text += self._generate_contributors(country_data_folder)
        header_text += (
            '======================================================='
        )
        return header_text

    def file(self):
        """Return file."""
        file = os.path.join(
            self.output_folder, '{}.zip'.format(str(self.uuid))
        )
        if os.path.exists(file):
            return file
        else:
            return None

    @property
    def age_hours(self):
        diff = timezone.now() - self.request_at
        return diff.total_seconds() / (60 * 60)

    def _generate_contributors(self, country_data_folder):
        """Generate readme."""
        header_text = (
            'Organisations contributing with groundwater '
            'monitoring data are:\r\n'
        )
        header_text += '\r\n'
        organisation_id = []
        if self.countries.exists():
            for country in self.countries.all():
                try:
                    organisation_id += self._get_organisations_in_countries(
                        country, country_data_folder
                    ).values_list('id', flat=True)
                except AttributeError:
                    pass
        elif self.organisations.exists():
            organisation_id += self.organisations.values_list('id', flat=True)

        organisation_id = list(set(organisation_id))
        for organisation in Organisation.objects.select_related(
                'country'
        ).filter(id__in=organisation_id).order_by('name'):
            _data = OrganisationContributorSerializer(organisation).data
            if organisation.country:
                header_text += f'{organisation.country.name} - '
            header_text += f'{organisation.name}'
            header_text += '\r\n'
            header_text += f'Data type : {_data["data_types"]}'
            header_text += '\r\n'
            header_text += f'Time range : {_data["time_range"]}'
            header_text += '\r\n'
            if organisation.license_data:
                header_text += f'License : {organisation.license_data.name}'
            else:
                header_text += f'License :  -'
            header_text += '\r\n'
            header_text += '\r\n'
        return header_text
