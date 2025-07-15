from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class LicenseMetadata(models.Model):
    """ Metadata for license"""
    restriction_code_type_help_text = _(
        'limitation(s) placed upon the access or use of the data. this is ID of restriction code in geonode.')
    constraints_other_help_text = _(
        'other restrictions and legal prerequisites for accessing and using the resource or'
        ' metadata')
    license_help_text = _(
        'license of the dataset. this is ID of license in geonode.'
    )

    restriction_code_type = models.IntegerField(
        verbose_name=_('Restrictions'),
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


class LicenseMetadataObject:
    """ License metadata for object """

    restriction_code_type = None
    license = None

    def __init__(
            self,
            obj: LicenseMetadata,
            convert=False
    ):
        """Init license metadata object."""
        from geonode.base.models import RestrictionCodeType, License
        self.constraints_other = obj.constraints_other
        self.restriction_code_type_id = obj.restriction_code_type
        self.license_id = obj.license
        if convert:
            # Get restriction code type
            try:
                self.restriction_code_type = RestrictionCodeType.objects.get(
                    id=self.restriction_code_type_id
                )
            except RestrictionCodeType.DoesNotExist:
                pass

            # Get license
            try:
                self.license = License.objects.get(
                    id=self.license_id
                )
            except License.DoesNotExist:
                pass

    @property
    def license_name(self):
        """Return license name."""
        if self.license:
            return self.license.name
        return '-'

    @property
    def restriction_code_type_name(self):
        """Return restriction_code_type name."""
        if self.restriction_code_type:
            return self.restriction_code_type.gn_description
        return '-'
