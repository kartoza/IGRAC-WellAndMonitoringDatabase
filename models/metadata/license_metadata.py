from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


class LicenseMetadata(models.Model):
    """ Metadata for license"""
    restriction_code_type_help_text = _(
        'limitation(s) placed upon the access or use of the data. this is ID of restriction code in geonode.')
    constraints_other_help_text = _(
        'other restrictions and legal prerequisites for accessing and using the resource or'
        ' metadata')
    license_help_text = _('license of the dataset. this is ID of license in geonode.')

    restriction_code_type = models.IntegerField(
        verbose_name=_('restrictions'),
        help_text=restriction_code_type_help_text,
        null=True,
        blank=True
    )
    constraints_other = models.TextField(
        _('restrictions other'),
        blank=True,
        null=True,
        help_text=constraints_other_help_text)
    license = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("License"),
        help_text=license_help_text)

    class Meta:
        abstract = True
