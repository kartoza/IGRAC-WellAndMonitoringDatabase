import uuid
from datetime import datetime

from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from gwml2.models.well import Well

User = get_user_model()

logger = get_task_logger(__name__)


class WellDeletion(models.Model):
    """Model contains well deletion."""

    user = models.IntegerField(
        null=True,
        blank=True
    )

    start_at = models.DateTimeField(
        default=datetime.now
    )
    identifier = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )
    ids = models.JSONField()
    data = models.JSONField()
    progress = models.IntegerField(default=0)

    @property
    def user_val(self):
        """ return user of uploader """
        try:
            return User.objects.get(id=self.user)
        except User.DoesNotExist:
            return None

    def run(self):
        """Run the process."""
        try:
            count = len(self.ids)
            for idx, id in enumerate(self.ids):
                logger.debug(f'{idx}/{count}')
                try:
                    well = Well.objects.get(id=id)
                    logger.debug(f'Deleting : {id}/{well.name}')
                    well.delete()
                except Well.DoesNotExist:
                    pass
                self.progress = ((idx + 1) / count) * 100
                if self.progress > 100:
                    self.progress = 100
                self.save()
            self.progress = 100
            self.save()
        except Exception as e:
            logger.debug(f'{e}')
