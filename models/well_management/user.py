import uuid
from django.contrib.gis.db import models


class UserUUID(models.Model):
    """ UserUUID
    """
    user_id = models.IntegerField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = 'user_uuid'
