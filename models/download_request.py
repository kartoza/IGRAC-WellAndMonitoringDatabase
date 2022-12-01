import os
import zipfile
from datetime import datetime
from uuid import uuid4

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from gwml2.models.general import Country

WELL_AND_MONITORING_DATA = 'Well and Monitoring Data'
GGMN = 'GGMN'


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

    def generate_file(self):
        """Generate file to be downloaded."""
        from gwml2.tasks.data_file_cache.country_recache import (
            GWML2_FOLDER, DATA_FOLDER
        )
        output_folder = os.path.join(
            GWML2_FOLDER, 'requests'
        )
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        request_file = os.path.join(
            output_folder, '{}.zip'.format(str(self.uuid))
        )
        zip_file = zipfile.ZipFile(request_file, 'w')
        for country in self.countries.all():
            unique_id = country.code
            data_file_name = f'{unique_id} - {self.data_type}.zip'
            data_file = os.path.join(
                DATA_FOLDER, data_file_name)
            if os.path.exists(data_file):
                zip_file.write(
                    data_file, data_file_name,
                    compress_type=zipfile.ZIP_DEFLATED)
        zip_file.close()

    def file(self):
        """Return file."""
        from gwml2.tasks.data_file_cache.country_recache import GWML2_FOLDER
        file = os.path.join(
            GWML2_FOLDER, 'requests', '{}.zip'.format(str(self.uuid))
        )
        if os.path.exists(file):
            return file
        else:
            return None
