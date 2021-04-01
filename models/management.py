from django.contrib.gis.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from gwml2.models.term import TermGroundwaterUse


class License(models.Model):
    """ License model """
    number = models.CharField(
        _('Number'),
        max_length=20,
        null=True,
        blank=True)
    valid_from = models.DateField(
        _('Valid from'),
        null=True,
        blank=True)
    valid_until = models.DateField(
        _('Valid until'),
        null=True,
        blank=True)
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True,
        help_text=_('Explain what the license entails.'))

    def __unicode__(self):
        return self.number

    class Meta:
        db_table = 'license'


class Management(models.Model):
    """ Management model """
    manager = models.CharField(
        verbose_name=_('Manager / owner'),
        max_length=200,
        null=True,
        blank=True,
        help_text=_('Name of the manager or owner of the groundwater point. '
                    'This can be a single person, a group of persons or an organisation.')
    )
    groundwater_use = models.ForeignKey(
        TermGroundwaterUse, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Groundwater use')
    )
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True,
        help_text=_('Explain how the groundwater point is managed.'))
    number_of_users = models.IntegerField(
        _('Number of people served'),
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('Indicate how many people use the groundwater.')
    )
    license = models.OneToOneField(
        License, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __unicode__(self):
        return self.manager

    class Meta:
        db_table = 'management'
