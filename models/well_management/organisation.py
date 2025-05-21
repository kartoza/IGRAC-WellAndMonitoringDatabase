from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _

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

    def save(self, *args, **kwargs):
        if self.pk:
            old = Organisation.objects.get(pk=self.pk)
            if old.name != self.name:
                self.update_ggis_uid()
        super().save(*args, **kwargs)

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

    def update_ggis_uid(self):
        """Update the id of the organisation """
        from gwml2.models.well import Well
        from django.db import transaction

        # Do it in batch
        BATCH_SIZE = 10000
        wells = list(self.well_set.all())
        for i in range(0, len(wells), BATCH_SIZE):
            batch = wells[i:i + BATCH_SIZE]
            for well in batch:
                well.update_ggis_uid()
            with transaction.atomic():
                Well.objects.bulk_update(batch, ['ggis_uid'])


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
