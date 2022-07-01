import os
import zipfile
from datetime import datetime
from uuid import uuid4

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from gwml2.models.general import Country
from gwml2.tasks.downloadable_well_cache import GWML2_FOLDER, DATA_FOLDER


class DownloadRequest(models.Model):
    """Request data to download the well data."""

    uuid = models.UUIDField(
        default=uuid4,
        editable=False
    )
    request_at = models.DateTimeField(
        _('Uploaded at'),
        default=datetime.now, blank=True
    )
    countries = models.ManyToManyField(
        Country,
        null=True, blank=True
    )
    name = models.CharField(
        _('Name'), max_length=512
    )
    surname = models.CharField(
        _('Surname'), null=True, blank=True, max_length=512
    )
    organisation = models.CharField(
        _('Organization'),
        max_length=512,
    )
    position = models.CharField(
        max_length=512
    )
    organisation_types = models.CharField(
        _('Type of organization'),
        max_length=512,
    )
    email = models.EmailField(_('email address'), blank=True)

    def generate_file(self):
        """Generate file to be downloaded."""
        output_folder = os.path.join(
            GWML2_FOLDER, 'request'
        )
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        request_file = os.path.join(
            output_folder, '{}.zip'.format(str(self.uuid))
        )
        zip_file = zipfile.ZipFile(request_file, 'w')
        for country in self.countries.all():
            unique_id = country.code
            data_file_name = '{}.zip'.format(str(unique_id))
            data_file = os.path.join(
                DATA_FOLDER, data_file_name)
            if os.path.exists(data_file):
                zip_file.write(
                    data_file, data_file_name,
                    compress_type=zipfile.ZIP_DEFLATED)
        zip_file.close()

    def file(self):
        """Return file."""
        file = os.path.join(
            GWML2_FOLDER, 'request', '{}.zip'.format(str(self.uuid))
        )
        if os.path.exists(file):
            return file
        else:
            return None
