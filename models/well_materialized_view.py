from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


class MaterializedViewWell(models.Model):
    """Data well from materialized view."""
    id = models.IntegerField(
        primary_key=True,
        null=False, blank=False,
    )
    ggis_uid = models.CharField(
        max_length=512, help_text=_('Organisation + id.'))

    original_id = models.CharField(
        max_length=512, help_text=_('As recorded in the original database.'))

    name = models.CharField(
        null=True, blank=True, max_length=512
    )
    feature_type = models.CharField(
        null=True, blank=True, max_length=512
    )
    purpose = models.CharField(
        null=True, blank=True, max_length=512
    )
    status = models.CharField(
        null=True, blank=True, max_length=512
    )
    organisation = models.CharField(
        null=True, blank=True, max_length=512
    )
    organisation_id = models.IntegerField(
        null=False, blank=False,
    )
    country = models.CharField(
        null=True, blank=True, max_length=512
    )

    year_of_drilling = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    aquifer_name = models.CharField(
        null=True, blank=True, max_length=512
    )
    aquifer_type = models.CharField(
        null=True, blank=True, max_length=512
    )
    manager = models.CharField(
        null=True, blank=True, max_length=512
    )
    detail = models.CharField(
        null=True, blank=True, max_length=512
    )
    location = models.PointField()
    created_at = models.DateTimeField(
        null=True, blank=True
    )
    created_by = models.IntegerField(
        null=True, blank=True
    )
    last_edited_at = models.DateTimeField(
        null=True, blank=True
    )
    last_edited_by = models.IntegerField(
        null=True, blank=True
    )
    number_of_measurements_level = models.IntegerField(
        null=False, blank=False,
    )
    number_of_measurements_quality = models.IntegerField(
        null=False, blank=False,
    )
    first_time_measurement = models.DateTimeField(
        null=True, blank=True
    )
    last_time_measurement = models.DateTimeField(
        null=True, blank=True
    )
    is_groundwater_level = models.CharField(
        null=True, blank=True, max_length=8
    )
    is_groundwater_quality = models.CharField(
        null=True, blank=True, max_length=8
    )

    def __str__(self):
        return self.ggis_uid

    class Meta:
        db_table = 'mv_well'
        managed = False
        ordering = ['original_id']
