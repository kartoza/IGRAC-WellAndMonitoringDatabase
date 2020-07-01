from django.contrib.gis.db import models


class Quantity(models.Model):
    """ Model to define quantity. """
    unit = models.TextField(
        null=True, blank=True)
    value = models.FloatField(
        null=True, blank=True)


class GWTerm(models.Model):
    """ Abstract model for Term """
    name = models.CharField(max_length=256)
    description = models.TextField()

    class Meta:
        abstract = True
