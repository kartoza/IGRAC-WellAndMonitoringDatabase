# coding=utf-8
"""Upload session model definition.

"""
import ntpath
import uuid
from datetime import datetime
from django.db import models
from gwml2.models.well_management.organisation import Organisation


class UploadSession(models.Model):
    """Upload session model
    """
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    uploader = models.IntegerField(
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        default=datetime.now
    )

    category = models.CharField(
        max_length=50,
        blank=True,
        default='',
    )

    status = models.TextField(
        blank=True,
        null=True
    )

    progress = models.IntegerField(
        default=0
    )

    upload_file = models.FileField(
        upload_to='gwml2/upload/',
        null=True
    )

    is_processed = models.BooleanField(
        default=False
    )

    is_canceled = models.BooleanField(
        default=False
    )

    # noinspection PyClassicStyleClass
    class Meta:
        """Meta class for project."""
        verbose_name_plural = 'Upload Sessions'
        verbose_name = 'Upload Session'
        ordering = ('-uploaded_at',)

    def __str__(self):
        return str(self.token)

    def filename(self):
        """ return filename """
        return ntpath.basename(self.upload_file.name)

    def update_progress(self, finished=False, status='', progress=0):
        """Update progress for current upload session

        :param finished: Whether the session is finished or not
        :type finished: bool

        :param status: Status message for current progress
        :type status: str

        :param progress: Current progress
        :type progress: int
        """
        if finished and progress == 100:
            self.is_processed = True
        if finished and progress < 100:
            self.is_canceled = True
        self.progress = progress
        self.status = status
        self.save()
