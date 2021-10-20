from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class CreationMetadata(models.Model):
    """ Metadata for creations"""
    created_at = models.DateTimeField(
        _('Created at'),
        default=timezone.now
    )
    created_by = models.IntegerField(
        _('Created by'),
        null=True, blank=True
    )
    last_edited_at = models.DateTimeField(
        _('Last edited at'),
        default=timezone.now
    )
    last_edited_by = models.IntegerField(
        _('Last edited by'),
        null=True, blank=True
    )

    class Meta:
        abstract = True

    def created_by_username(self):
        """ Return username of creator """
        if not self.created_by:
            return '-'
        try:
            return User.objects.get(id=self.created_by).username
        except User.DoesNotExist:
            return '-'

    def last_edited_by_username(self):
        """ Return username of last updater """
        if not self.last_edited_by:
            return '-'
        try:
            return User.objects.get(id=self.last_edited_by).username
        except User.DoesNotExist:
            return '-'
