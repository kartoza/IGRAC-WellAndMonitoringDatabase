from django.contrib.gis.db import models


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


class Quantity(models.Model):
    """ Model to define quantity. """
    value = models.FloatField(
        null=True, blank=True)
    unit = models.CharField(
        null=True, blank=True, max_length=128)

    def __str__(self):
        return '{} ({})'.format(self.value, self.unit)
