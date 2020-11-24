# coding=utf-8
"""Upload session model definition.

"""
import json
import os
import ntpath
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models
from gwml2.models.well_management.organisation import Organisation

UPLOAD_SESSION_CATEGORY_WELL_UPLOAD = 'well_upload'
UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD = 'well_monitoring_upload'

# make choices
UPLOAD_SESSION_CATEGORY = (
    (UPLOAD_SESSION_CATEGORY_WELL_UPLOAD, UPLOAD_SESSION_CATEGORY_WELL_UPLOAD),
    (UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD, UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD),
)


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
        choices=UPLOAD_SESSION_CATEGORY,
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

    def progress_status(self):
        """
        return progress status
        if there is file of progress
        else return from model value itself
        """
        try:
            _file = open(os.path.join(
                settings.MEDIA_ROOT, 'gwml2', 'upload', 'progress', str(self.token)
            ))
            return json.loads(_file.read())
        except Exception:
            return {
                'progress': self.progress,
                'status': self.status
            }

    def update_progress(self, finished=False, status='', progress=0):
        """Update progress for current upload session

        :param finished: Whether the session is finished or not
        :type finished: bool

        :param status: Status message for current progress
        :type status: str

        :param progress: Current progress
        :type progress: int
        """

        folder = os.path.join(
            settings.MEDIA_ROOT, 'gwml2', 'upload', 'progress'
        )
        if finished:
            if progress == 100:
                self.is_processed = True
            if progress < 100:
                self.is_canceled = True
            if os.path.exists(os.path.join(folder, str(self.token))):
                os.remove(os.path.join(folder, str(self.token)))
        else:
            try:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                f = open(os.path.join(folder, str(self.token)), "w+")
                f.write(json.dumps({
                    'progress': progress,
                    'status': status
                }))
                f.close()
            except Exception as e:
                pass

        self.progress = progress
        self.status = status
        self.save()
