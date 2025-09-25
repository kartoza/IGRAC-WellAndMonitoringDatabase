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

    # Data cache information
    data_cache_information = models.JSONField(
        help_text=_(
            'Information about the data cache, '
            'like the time of file is being generated.'
        ),
        null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
        verbose_name = 'Country'
        ordering = ('name',)
        db_table = 'country'

    def assign_data_cache_information(self):
        """Assign data cache information.
        We not use this on generator, just on the django admin command.
        """
        from gwml2.tasks.data_file_cache.country_recache import (
            COUNTRY_DATA_FOLDER
        )
        from gwml2.models.download_request import (
            WELL_AND_MONITORING_DATA, GGMN
        )
        self.data_cache_information = {}
        cache_name = self.code
        for data_type in [WELL_AND_MONITORING_DATA, GGMN]:
            zip_filename = f'{cache_name} - {data_type}.zip'
            file_path = os.path.join(COUNTRY_DATA_FOLDER, zip_filename)
            if os.path.exists(file_path):
                file = os.path.basename(file_path).split('-')[1]
                modified_time = os.path.getmtime(file_path)
                readable_time = datetime.fromtimestamp(modified_time)
                self.data_cache_information[file] = (
                    readable_time.strftime('%Y-%m-%d %H:%M:%S')
                )
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
