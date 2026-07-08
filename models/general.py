import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from gwml2.models.term import _Term

User = get_user_model()


class Country(models.Model):
    """ Country model"""
    name = models.CharField(
        max_length=512
    )
    code = models.CharField(
        max_length=126
    )
    geometry = models.MultiPolygonField(
        null=True, blank=True
    )
    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )

    # Metadata cache
    metadata_cache_observations_repository = models.JSONField(
        help_text=_(
            'Cached statistics for this country for '
            'Groundwater Observations Repository.'
        ),
        null=True, blank=True
    )
    metadata_cache_ggmn = models.JSONField(
        help_text=_('Cached statistics for this country for GGMN.'),
        null=True, blank=True
    )
    metadata_cache_generated_at = models.DateTimeField(
        _('Time when metadata cache were generated'),
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
        verbose_name = 'Country'
        ordering = ('name',)
        db_table = 'country'

    def assign_metadata_cache(self):
        """Assign data cache generated at based on zip file modification time."""
        from gwml2.tasks.well_file_cache.country_recache import (
            COUNTRY_DATA_FOLDER
        )
        zip_file = os.path.join(COUNTRY_DATA_FOLDER, f'{self.code}.zip')
        if os.path.exists(zip_file):
            self.data_cache_generated_at = datetime.fromtimestamp(
                os.path.getmtime(zip_file)
            )
        else:
            self.data_cache_generated_at = None
        Country.objects.filter(pk=self.pk).update(
            data_cache_generated_at=self.data_cache_generated_at
        )
        self._generate_metadata_cache()

    def _generate_metadata_cache(self):
        """Assign date range and count measurements and wells."""
        from django.utils import timezone
        from gwml2.utils.metadata_cache import generate_metadata_cache
        from gwml2.models.well_management.organisation import (
            OrganisationGroup
        )

        # Check for global
        print(f'Generate metadata cache for country {self.name}')

        ggmn_group = OrganisationGroup.get_ggmn_group()

        print(
            f'Generate metadata cache for country {self.name} -'
            f'Groundwater Observations Repository'
        )
        self.metadata_cache_generated_at = timezone.now()
        print(f'Generate metadata cache for country {self.name} - GGMN')
        wells = self.well_set.filter(
            organisation__active=True
        )
        if ggmn_group:
            repository_well_ids = wells.exclude(
                organisation__in=ggmn_group.organisations.all()
            ).values_list('id', flat=True)
        else:
            repository_well_ids = wells.values_list('id', flat=True)
        cache = generate_metadata_cache(repository_well_ids)
        Country.objects.filter(pk=self.pk).update(
            metadata_cache_observations_repository=cache.get_json(),
            metadata_cache_generated_at=self.metadata_cache_generated_at,
        )

        print(f'Generate metadata cache for country {self.name} - GGMN')
        if ggmn_group:
            well_ids = wells.filter(
                organisation__in=ggmn_group.organisations.all()
            ).values_list('id', flat=True)
            cache = generate_metadata_cache(well_ids)

            self.metadata_cache_generated_at = timezone.now()
            Country.objects.filter(pk=self.pk).update(
                metadata_cache_ggmn=cache.get_json(),
                metadata_cache_generated_at=self.metadata_cache_generated_at,
            )


class Unit(_Term):
    """ List of unit."""
    html = models.CharField(
        max_length=512,
        null=True, blank=True
    )

    def __str__(self):
        return self.html if self.html else self.name

    class Meta:
        db_table = 'unit'
        ordering = ('name',)


class UnitConvertion(models.Model):
    """ This model about formula for converting unit """
    unit_from = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='unit_convertion_unit_from'
    )
    unit_to = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='unit_convertion_unit_to'
    )
    formula = models.CharField(
        max_length=512,
        help_text='Use x as parameters for value from an unit.'
                  'Example: m to cm, fill x*1000'
    )

    class Meta:
        db_table = 'unit_conversion'
        unique_together = ('unit_from', 'unit_to')


class UnitGroup(_Term):
    """ Group of unit."""
    units = models.ManyToManyField(
        Unit,
        null=True, blank=True
    )

    class Meta:
        db_table = 'unit_group'
        ordering = ('name',)


class Quantity(models.Model):
    """ Model to define quantity. """
    unit = models.ForeignKey(
        Unit,
        null=True, blank=True,
        on_delete=models.SET_NULL)
    value = models.FloatField()

    def __str__(self):
        if self.unit:
            return '{} {}'.format(self.value, self.unit)
        else:
            return '{}'.format(self.value)

    class Meta:
        verbose_name_plural = 'Quantities'
        verbose_name = 'Quantity'
        db_table = 'quantity'

    def convert(self, to):
        """ this is converter value from unit into to
        :param to:
        :type to: str
        """
        if self.unit and (
                self.unit.name == 'ft' or self.unit.name == 'ft') and to == 'm':
            self.unit.name = to
            return self.value / 3.281
        return self.value
