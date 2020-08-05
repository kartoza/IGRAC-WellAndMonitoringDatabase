from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from gwml2.models.term import TermGroundwaterUse


class License(models.Model):
    """ License model """
    number = models.TextField()
    valid_from = models.DateField()
    valid_until = models.DateField()
    description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return self.number


class Management(models.Model):
    """ Management model """
    manager = models.CharField(
        verbose_name='Manager/owner',
        max_length=512
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
        verbose_name='Number of users/beneficiaries'
    )
    license = models.ForeignKey(
        License, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __unicode__(self):
        return self.manager
