from django.contrib.gis.db import models


class WellWithUUID(models.Model):
    """ Return view : well_with_uuid
    """
    original_id = models.CharField(
        null=True, blank=True, max_length=256
    )
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
    country = models.CharField(
        null=True, blank=True, max_length=512
    )
    year_of_drilling = models.CharField(
        null=True, blank=True, max_length=512
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
    location = models.PointField(
        verbose_name="location",
        help_text="Location of the feature."
    )
    uuid = models.CharField(
        null=True, blank=True, max_length=512
    )
    detail = models.CharField(
        null=True, blank=True, max_length=512
    )
    public = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'well_with_uuid'
        managed = False
