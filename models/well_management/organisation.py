from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


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

    # for the permission
    admins = ArrayField(
        models.IntegerField(), default=list, null=True)
    editors = ArrayField(
        models.IntegerField(), default=list, null=True)

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
