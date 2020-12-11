import uuid
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

User = get_user_model()


class UserUUID(models.Model):
    """ UserUUID  """
    user_id = models.IntegerField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(
        max_length=150, null=True, blank=True
    )

    class Meta:
        db_table = 'user_uuid'

    def update_username(self):
        try:
            self.username = User.objects.get(id=self.user_id).username
            self.save()
        except User.DoesNotExist:
            pass
