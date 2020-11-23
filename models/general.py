from django.contrib.gis.db import models
from adminsortable.models import Sortable
from gwml2.models.term import _Term


class Country(models.Model):
    """ Country model"""
    name = models.CharField(
        max_length=512)
    code = models.CharField(
        max_length=126)
    geometry = models.MultiPolygonField(
        null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
        verbose_name = 'Country'
        ordering = ('name',)
        db_table = 'country'


class Unit(_Term):
    """ List of unit."""
    html = models.CharField(
        max_length=512,
        null=True, blank=True
    )

    def __str__(self):
        return self.html if self.html else self.name

    class Meta(Sortable.Meta):
        db_table = 'unit'


class UnitGroup(_Term):
    """ Group of unit."""
    units = models.ManyToManyField(
        Unit,
        null=True, blank=True
    )

    class Meta(Sortable.Meta):
        db_table = 'unit_group'


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
        if (self.unit.name == 'ft' or self.unit.name == 'ft') and to == 'm':
            return self.value / 3.281
        return self.value
