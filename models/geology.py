__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '27/08/20'

from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermReferenceElevationType
from django.utils.translation import ugettext_lazy as _


class Geology(models.Model):
    """ Geology
    """
    total_depth = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text=_('Depth of the well below the ground surface.'),
        verbose_name=_('Total depth')
    )
    reference_elevation = models.ForeignKey(
        TermReferenceElevationType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Total depth reference elevation')
    )

    class Meta:
        db_table = 'geology'
