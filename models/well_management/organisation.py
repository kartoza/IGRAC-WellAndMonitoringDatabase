from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Country
from gwml2.models.metadata.license_metadata import LicenseMetadata


class Organisation(LicenseMetadata):
    """Organisation."""

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

    wagtail_reference_index_ignore = True
    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )

    # Data metadata
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

    # Data type
    data_is_groundwater_level = models.BooleanField(
        default=False
    )
    data_is_groundwater_quality = models.BooleanField(
        default=False
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
        """Return list of data types"""
        data_types = []
        if self.data_is_groundwater_level:
            data_types.append('Groundwater levels')
        if self.data_is_groundwater_quality:
            data_types.append('Groundwater quality')
        return data_types

    @property
    def time_range(self):
        """Return time range indicator."""
        if self.data_is_from_api:
            return 'Updated automatically (via API)'
        if self.data_date_start and self.data_date_end:
            start = self.data_date_start.strftime('%Y-%m')
            end = self.data_date_end.strftime('%Y-%m')
            return f'start: {start}; end: {end}'
        return ''

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

    def assign_data_types(self):
        """Assign data types to this organisation based on current data."""
        from gwml2.models import (
            WellLevelMeasurement, WellQualityMeasurement
        )
        self.data_is_groundwater_level = WellLevelMeasurement.objects.filter(
            well__organisation=self
        ).exists()
        self.data_is_groundwater_quality = WellQualityMeasurement.objects.filter(
            well__organisation=self
        ).exists()
        self.save()

    def assign_date_range(self):
        """Assign date range to this organisation based on current data."""
        from gwml2.models import (
            Harvester, WellLevelMeasurement, WellQualityMeasurement,
            WellYieldMeasurement
        )

        # Data is from API
        data_is_from_api = Harvester.objects.filter(
            organisation=self
        ).exists()
        self.data_is_from_api = data_is_from_api
        self.save()

        if not data_is_from_api:
            # --------------------------------
            # Get for time range
            # --------------------------------
            # Get dates from level measurements
            level_dates = WellLevelMeasurement.objects.filter(
                well__organisation=self
            ).aggregate(
                min_date=models.Min('time'),
                max_date=models.Max('time')
            )
            # Get dates from quality measurements
            quality_dates = WellQualityMeasurement.objects.filter(
                well__organisation=self
            ).aggregate(
                min_date=models.Min('time'),
                max_date=models.Max('time')
            )
            # Get dates from quality measurements
            yield_dates = WellYieldMeasurement.objects.filter(
                well__organisation=self
            ).aggregate(
                min_date=models.Min('time'),
                max_date=models.Max('time')
            )

            start_dates = []
            end_dates = []
            if level_dates['min_date']:
                start_dates.append(level_dates['min_date'])
                end_dates.append(level_dates['max_date'])
            if quality_dates['min_date']:
                start_dates.append(quality_dates['min_date'])
                end_dates.append(quality_dates['max_date'])
            if yield_dates['min_date']:
                start_dates.append(yield_dates['min_date'])
                end_dates.append(yield_dates['max_date'])

            if start_dates:
                self.data_date_start = min(start_dates)
            if end_dates:
                self.data_date_end = max(end_dates)
            self.save()

    def assign_data(self):
        """Automatically assign data to this
        organization based on current data."""
        self.assign_data_types()
        self.assign_date_range()


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
    from gwml2.tasks.data_file_cache.country_recache import (
        generate_data_all_country_cache
    )
    from gwml2.tasks.data_file_cache.organisation_cache import (
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
