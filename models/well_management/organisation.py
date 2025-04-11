from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from gwml2.models.general import Country


class Organisation(models.Model):
    """ Organisation
    """

    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    # this is for ordering
    order = models.PositiveIntegerField(
        default=0, editable=False, db_index=True
    )
    active = models.BooleanField(
        default=True,
        help_text='If not active, all well under it will be hidden'
    )

    # for the permission
    admins = ArrayField(
        models.IntegerField(), default=list, null=True)
    editors = ArrayField(
        models.IntegerField(), default=list, null=True)

    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL,
        help_text=(
            'Identify the country of the organisation. '
            "It is being used to assign well's country under "
            "this organisation. "
            'If this is empty, all well under this organisation '
            'will be assigned based on geometry of country.'
        )
    )

    wagtail_reference_index_ignore = True
    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )

    class Meta:
        db_table = 'organisation'
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_admin(self, user):
        """ return if admin """
        return user.is_superuser or user.is_staff or user.id in self.admins

    def is_editor(self, user):
        """ return if editor """
        return self.is_admin(user) or user.id in self.editors

    @staticmethod
    def ggmn_organisations() -> list[int]:
        """Return list of organisation id"""
        from igrac.models.groundwater_layer import GroundwaterLayer
        ggmn_organisations_list = list(
            Organisation.objects.filter(
                active=True
            ).values_list('id', flat=True)
        )
        ggmn_layer = GroundwaterLayer.objects.filter(
            is_ggmn_layer=True).first()
        if ggmn_layer:
            ggmn_organisations_list = ggmn_layer.organisations
        return ggmn_organisations_list


class OrganisationType(models.Model):
    """ Organisation type
    """
    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'organisation_type'
        ordering = ['name']

    def __str__(self):
        return self.name
