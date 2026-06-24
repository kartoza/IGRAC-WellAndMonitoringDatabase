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
        max_length=512)
    code = models.CharField(
        max_length=126)
    geometry = models.MultiPolygonField(
        null=True, blank=True)
    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
        verbose_name = 'Country'
        ordering = ('name',)
        db_table = 'country'

    def assign_data(self):
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
        self.save()


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
