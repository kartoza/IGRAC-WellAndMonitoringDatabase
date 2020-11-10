# coding=utf-8
"""Download session model definition.

"""
import os
import uuid
from datetime import datetime
from django.db import models
from django.dispatch import receiver


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

    uploaded_at = models.DateTimeField(
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

    # noinspection PyClassicStyleClass
    class Meta:
        """Meta class for project."""
        verbose_name_plural = 'Download Sessions'
        verbose_name = 'Download Session'
        ordering = ('-uploaded_at',)
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


@receiver(models.signals.post_delete, sender=DownloadSession)
def download_session_deleted(sender, instance, **kwargs):
    """
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
