# coding=utf-8
"""Download session model definition.

"""
import json
import os
import uuid
from datetime import datetime
from django.db import models
from django.dispatch import receiver
from gwml2.models.well import Well


class DownloadSession(models.Model):
    """Download session model
    """
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    filters = models.TextField(
        blank=True,
        null=True
    )

    start_at = models.DateTimeField(
        default=datetime.now
    )

    progress = models.IntegerField(
        default=0
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    file = models.FileField(
        blank=True,
        null=True
    )

    obsolete = models.BooleanField(
        default=False
    )

    well = models.ForeignKey(
        Well,
        null=True, blank=True, on_delete=models.CASCADE
    )

    # noinspection PyClassicStyleClass
    class Meta:
        """Meta class for project."""
        verbose_name_plural = 'Download Sessions'
        verbose_name = 'Download Session'
        ordering = ('-start_at',)
        db_table = 'download_session'

    def __str__(self):
        return str(self.token)

    def update_progress(self, progress=0, notes=None):
        """Update progress for current upload session

        :param progress: Current progress
        :type progress: int

        :param notes: Additional notes
        :type notes: dict
        """
        self.progress = progress
        self.notes = notes
        self.save()


class DownloadSessionUser(models.Model):
    """Download session user model
    """
    session = models.ForeignKey(
        DownloadSession, on_delete=models.CASCADE
    )

    user = models.IntegerField(
        null=True,
        blank=True
    )

    # noinspection PyClassicStyleClass
    class Meta:
        """Meta class for project."""
        verbose_name_plural = 'Download Sessions User'
        verbose_name = 'Download Session User'
        db_table = 'download_session_user'

    def get_info(self):
        return '\n;'.join([
            '{} : {}'.format(key, value) for key, value in json.loads(self.session.filters).items()
        ])


@receiver(models.signals.post_delete, sender=DownloadSession)
def download_session_deleted(sender, instance, **kwargs):
    """
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
