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
        ordering = ('name',)
        db_table = 'country'


class Unit(_Term):
    """ List of unit."""
    html = models.CharField(
        max_length=512,
        null=True, blank=True
    )

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
        return '{} ({})'.format(self.value, self.unit)

    class Meta:
        db_table = 'quantity'
