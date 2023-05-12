import os
import shutil
import zipfile
from datetime import datetime
from uuid import uuid4

from django.conf import settings
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

    output_folder = os.path.join(settings.MEDIA_ROOT, 'request')

    def generate_file(self):
        """Generate file to be downloaded."""
        from gwml2.tasks.data_file_cache.country_recache import DATA_FOLDER
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        is_world = False
        if self.countries.count() == Country.objects.count():
            is_world = True

        request_file = os.path.join(
            self.output_folder, '{}.zip'.format(str(self.uuid))
        )

        # If world, we need to check the file is latest or not
        # If there is file is latest than cache, regenerate
        if is_world:
            is_latest = True
            world_file_name = f'WORLD - {self.data_type}.zip'
            world_file = os.path.join(DATA_FOLDER, world_file_name)
            if os.path.exists(world_file):
                world_time = os.path.getmtime(world_file)

                # We check if data is updated
                for country in self.countries.all():
                    data_file_name = f'{country.code} - {self.data_type}.zip'
                    data_file = os.path.join(DATA_FOLDER, data_file_name)
                    if os.path.exists(data_file):
                        data_time = os.path.getmtime(data_file)
                        if world_time < data_time:
                            is_latest = False

                # If world is still latest, just use cache
                if is_latest:
                    shutil.copyfile(world_file, request_file)
                    return

        zip_file = zipfile.ZipFile(request_file, 'w')
        for country in self.countries.all():
            data_file_name = f'{country.code} - {self.data_type}.zip'
            data_file = os.path.join(DATA_FOLDER, data_file_name)
            if os.path.exists(data_file):
                zip_file.write(
                    data_file, data_file_name,
                    compress_type=zipfile.ZIP_DEFLATED
                )
        zip_file.close()

        # if is_world
        if is_world:
            data_file_name = f'WORLD - {self.data_type}.zip'
            data_file = os.path.join(DATA_FOLDER, data_file_name)
            shutil.copyfile(request_file, data_file)

    def file(self):
        """Return file."""
        file = os.path.join(
            self.output_folder, '{}.zip'.format(str(self.uuid))
        )
        if os.path.exists(file):
            return file
        else:
            return None
