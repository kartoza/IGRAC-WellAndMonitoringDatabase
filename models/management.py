from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from gwml2.models.term import TermGroundwaterUse


class License(models.Model):
    """ License model """
    number = models.CharField(
        max_length=512,
        null=True,
        blank=True)
    valid_from = models.DateField(
        null=True,
        blank=True)
    valid_until = models.DateField(
        null=True,
        blank=True)
    description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return self.number

    class Meta:
        db_table = 'license'


class Management(models.Model):
    """ Management model """
    manager = models.CharField(
        verbose_name='Manager / owner',
        max_length=512,
        null=True,
        blank=True
    )
    description = models.TextField(
        null=True,
        blank=True)

    groundwater_use = models.ForeignKey(
        TermGroundwaterUse, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    number_of_users = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Number of users / beneficiaries'
    )
    license = models.ForeignKey(
        License, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __unicode__(self):
        return self.manager

    class Meta:
        db_table = 'management'
