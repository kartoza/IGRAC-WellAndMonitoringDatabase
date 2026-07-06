from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Country
from gwml2.models.metadata.license_metadata import LicenseMetadata
from gwml2.utils.metadata_cache import MetadataCache


class Organisation(LicenseMetadata):
    """Organisation."""

    wagtail_reference_index_ignore = True

    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    # this is for ordering
    order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )
    active = models.BooleanField(
        default=True,
        help_text='If not active, all well under it will be hidden'
    )

    # for the permission
    admins = ArrayField(
        models.IntegerField(), default=list, null=True)
    editors = ArrayField(
        models.IntegerField(), default=list, null=True)

    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL,
        help_text=(
            'Identify the country of the organisation. '
            "It is being used to assign well's country under "
            "this organisation. "
            'If this is empty, all well under this organisation '
            'will be assigned based on geometry of country.'
        )
    )

    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )

    # Metadata cache
    data_is_from_api = models.BooleanField(
        default=False,
        help_text=(
            'If true, this organisation data is created from API.'
            'For telling the timerange is Updated automatically (via API).'
        )
    )
    data_date_start = models.DateField(
        null=True, blank=True
    )
    data_date_end = models.DateField(
        null=True, blank=True
    )
    data_stats = models.JSONField(
        help_text=_(
            'Cached statistics for this organisation: '
            'measurement counts (total, per type, midnight) '
            'and well counts (total, with level/quality data, springs).'
        ),
        null=True, blank=True
    )
    metadata_cache_generated_at = models.DateTimeField(
        _('Time when metadata cache were generated'),
        null=True, blank=True
    )

    class Meta:
        db_table = 'organisation'
        ordering = ['name']

    def save(self, *args, **kwargs):
        updated = False
        if self.pk:
            old = Organisation.objects.get(pk=self.pk)
            if old.name != self.name:
                updated = True
        super().save(*args, **kwargs)
        if updated:
            self.update_ggis_uid_background()

    @property
    def data_types(self):
        """Return list of data types derived from data_stats."""
        cache = self.metadata_cache
        data_types = []
        if cache.count_measurement_level:
            data_types.append('Groundwater levels')
        if cache.count_measurement_quality:
            data_types.append('Groundwater quality')
        return data_types

    @property
    def time_range(self):
        """Return time range indicator."""
        current = ''
        if self.data_date_start and self.data_date_end:
            start = self.data_date_start.strftime('%Y-%m')
            end = self.data_date_end.strftime('%Y-%m')
            current = f'start: {start}; end: {end}'
        if self.data_is_from_api:
            return (
                "Updated automatically (via API) "
                f"{'- current ' + current if current else ''}"
            )
        return current

    def __str__(self):
        return self.name

    def is_admin(self, user):
        """ return if admin """
        return user.is_superuser or user.is_staff or user.id in self.admins

    def is_editor(self, user):
        """ return if editor """
        return self.is_admin(user) or user.id in self.editors

    @property
    def license_data(self):
        """Return license name."""
        from geonode.base.models import License
        try:
            if self.license:
                return License.objects.get(id=self.license)
        except License.DoesNotExist:
            pass
        return None

    @property
    def metadata_cache(self) -> MetadataCache:
        """Metadata cache"""
        stats = self.data_stats or {}
        return MetadataCache(
            data_date_start=self.data_date_start,
            data_date_end=self.data_date_end,
            **stats
        )

    def update_ggis_uid_background(self):
        """Update the id of the organisation """
        from gwml2.tasks.organisation import update_ggis_uid
        update_ggis_uid.delay(self.pk)

    def update_ggis_uid(self):
        """Update the id of the organisation """
        from gwml2.models.well import Well
        from django.db import transaction
        print(f'Update GGIS UID for organisation {self.name}')

        # Do it in batch
        BATCH_SIZE = 10000
        wells = list(self.well_set.all())
        for i in range(0, len(wells), BATCH_SIZE):
            batch = wells[i:i + BATCH_SIZE]
            for well in batch:
                well.update_ggis_uid()
            with transaction.atomic():
                Well.objects.bulk_update(batch, ['ggis_uid'])

    # -------------------------------------
    # Assign data
    # -------------------------------------
    def assign_metadata_cache(self, generate_midnight=False):
        """Automatically assign data to this
        organization based on current data."""
        import os
        from datetime import datetime
        from gwml2.tasks.well_file_cache.organisation_cache import (
            ORGANISATION_DATA_FOLDER
        )
        zip_file = os.path.join(ORGANISATION_DATA_FOLDER, f'{self.name}.zip')
        if os.path.exists(zip_file):
            self.data_cache_generated_at = datetime.fromtimestamp(
                os.path.getmtime(zip_file)
            )
        else:
            self.data_cache_generated_at = None
        Organisation.objects.filter(pk=self.pk).update(
            data_cache_generated_at=self.data_cache_generated_at
        )
        self._generate_metadata_cache(generate_midnight)


    def _generate_metadata_cache(self, generate_midnight=False):
        """Assign date range and count measurements and wells."""
        from django.utils import timezone
        from gwml2.models import Harvester
        from gwml2.utils.metadata_cache import generate_metadata_cache

        self.data_is_from_api = Harvester.objects.filter(
            organisation=self
        ).exists()

        well_ids = self.well_set.values_list('id', flat=True)
        cache = generate_metadata_cache(
            well_ids, generate_midnight=generate_midnight
        )

        stats = cache.get_json(generate_midnight)
        self.data_date_start = cache.data_date_start
        self.data_date_end = cache.data_date_end
        self.data_stats = {**(self.data_stats or {}), **stats}
        self.metadata_cache_generated_at = timezone.now()
        Organisation.objects.filter(pk=self.pk).update(
            data_is_from_api=self.data_is_from_api,
            data_date_start=self.data_date_start,
            data_date_end=self.data_date_end,
            data_stats=self.data_stats,
            metadata_cache_generated_at=self.metadata_cache_generated_at,
        )


class OrganisationLink(models.Model):
    """Organisation link model."""
    organisation = models.ForeignKey(
        'Organisation',
        on_delete=models.CASCADE,
        related_name='links'
    )
    name = models.CharField(max_length=512)
    url = models.URLField(
        max_length=512,
        help_text='URL of the organisation link'
    )

    class Meta:
        db_table = 'organisation_link'

    def __str__(self):
        return f"{self.organisation.name} - {self.url}"


class OrganisationGroup(models.Model):
    """Organisation group model.."""
    name = models.CharField(max_length=512)
    organisations = models.ManyToManyField(
        'Organisation',
        related_name='groups',
        blank=True
    )
    download_readme_text = models.TextField(
        blank=True,
        null=True,
        help_text=(
            'Readme text to be included in the download zip file.'
        )
    )

    class Meta:
        db_table = 'organisation_group'

    def __str__(self):
        return self.name

    @staticmethod
    def get_ggmn_group():
        """Get ggmn group."""
        return OrganisationGroup.objects.filter(
            name__icontains='ggmn'
        ).first()


class OrganisationType(models.Model):
    """ Organisation type."""
    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'organisation_type'
        ordering = ['name']

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=OrganisationGroup.organisations.through)
def groundwater_layer_saved(
        sender, instance: OrganisationGroup, using, **kwargs
):
    from igrac.models.groundwater_layer import GroundwaterLayer
    from gwml2.tasks.well_file_cache.country_recache import (
        generate_data_all_country_cache
    )
    from gwml2.tasks.well_file_cache.organisation_cache import (
        generate_data_all_organisation_cache
    )
    try:
        action = kwargs['action']
    except KeyError:
        action = None
    if action in ['post_add', 'post_remove', 'post_clear']:
        if instance == OrganisationGroup.get_ggmn_group():
            generate_data_all_country_cache.delay()
            generate_data_all_organisation_cache.delay()

        # Update the layer
        for layer in GroundwaterLayer.objects.filter(
                organisation_groups__contains=[instance.id]
        ):
            layer.update_layer(layer.all_organisations, layer.additional_sql)
