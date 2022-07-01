from django.contrib.auth import get_user_model
from django.db.utils import ProgrammingError

from gwml2.models.well_management.user import UserUUID
from .construction import *
from .document import *
from .drilling import *
from .geology import *
from .hydrogeology import *
from .management import *
from .well import *

User = get_user_model()


@receiver(post_save, sender=User)
def user_saved(sender, instance, **kwargs):
    try:
        UserUUID.objects.get_or_create(user_id=instance.id, defaults={
            'username': instance.username
        })
    except ProgrammingError:
        pass
