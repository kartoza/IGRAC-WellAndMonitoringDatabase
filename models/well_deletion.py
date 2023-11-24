import uuid
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

User = get_user_model()


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
