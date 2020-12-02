from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from adminsortable.models import Sortable
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


class CreationMetadata(models.Model):
    """ List of unit."""
    created_at = models.DateTimeField(
        default=datetime.now
    )
    created_by = models.IntegerField(
        null=True, blank=True
    )
    last_edited_at = models.DateTimeField(
        default=datetime.now
    )
    last_edited_by = models.IntegerField(
        null=True, blank=True
    )

    class Meta:
        abstract = True

    def created_by_username(self):
        """ Return username of creator """
        if not self.created_by:
            return '-'
        try:
            return User.objects.get(id=self.created_by).username
        except User.DoesNotExist:
            return '-'

    def last_edited_by_username(self):
        """ Return username of last updater """
        if not self.last_edited_by:
            return '-'
        try:
            return User.objects.get(id=self.last_edited_by).username
        except User.DoesNotExist:
            return '-'


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
