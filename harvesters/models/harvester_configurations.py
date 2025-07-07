from django.db import models
from preferences.models import Preferences


class HarvesterPreference(Preferences):
    """Model to define site preferences."""

    run_harvester_at_same_time = models.IntegerField(
        default=3,
    )
