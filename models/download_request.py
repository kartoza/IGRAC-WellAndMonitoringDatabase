import os
import zipfile
import json
from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from gwml2.models.general import Country
from gwml2.models.well_management.organisation import Organisation
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
        default='Well and Monitoring Data',
        choices=(
            (WELL_AND_MONITORING_DATA, WELL_AND_MONITORING_DATA),
            (GGMN, GGMN),
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

    def generate_file(self):
        """Generate file to be downloaded."""
        from gwml2.tasks.data_file_cache.country_recache import DATA_FOLDER
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        request_file = os.path.join(
            self.output_folder, '{}.zip'.format(str(self.uuid))
        )

        zip_file = zipfile.ZipFile(request_file, 'w')
        for country in self.countries.all():
            data_file_name = f'{country.code} - {self.data_type}.zip'
            data_file = os.path.join(DATA_FOLDER, data_file_name)
            if os.path.exists(data_file):
                zip_file.write(
                    data_file, data_file_name,
                    compress_type=zipfile.ZIP_DEFLATED
                )
        zip_file.writestr('Readme.txt',
                          self._generate_readme_file(DATA_FOLDER))
        zip_file.close()

        # Make this downloader done
        self.is_ready = True
        self.save()

    def _get_readme_text(self):
        pref = SitePreference.objects.first()
        if pref is None:
            return DEFAULT_README_HEADER_TEXT
        header_text = ''
        if self.data_type == GGMN:
            header_text = pref.ggmn_download_readme_text
        else:
            header_text = pref.download_readme_text
        return header_text if header_text else DEFAULT_README_HEADER_TEXT

    def _generate_readme_file(self, data_folder):
        header_text = self._get_readme_text()
        header_text += '\r\n'
        header_text += '\r\n'
        header_text += (
            'Organisations contributing with groundwater '
            'monitoring data are:\r\n'
        )
        for country in self.countries.all():
            _organisation_file_name = (
                f'{country.code} - {self.data_type}.json'
            )
            _file_path = os.path.join(data_folder, _organisation_file_name)
            if not os.path.exists(_file_path):
                continue
            data = []
            with open(_file_path, "r") as _file:
                data = json.loads(_file.read())
            if len(data) == 0:
                continue
            _organisation_str = ', '.join(data)
            header_text += f'{country.name} - {_organisation_str};\r\n'
        header_text += '\r\n'
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
