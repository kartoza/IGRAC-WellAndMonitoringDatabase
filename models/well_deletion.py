import uuid
from datetime import datetime

from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.db.models.signals import post_delete

from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement
)

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
    note = models.TextField(blank=True)

    @property
    def user_val(self):
        """ return user of uploader """
        try:
            return User.objects.get(id=self.user)
        except User.DoesNotExist:
            return None

    def update_note(self, text):
        """Update note."""
        self.note = text
        self.save()

    def delete_measurement(self, query, title):
        """Delete measurement."""
        ids = query.values_list('id', flat=True)
        self.update_note(
            f'Deleting : {title} : {len(ids)}'
        )
        for id in ids:
            try:
                query.get(id=id).delete()
            except WellLevelMeasurement.DoesNotExist:
                pass
            except WellYieldMeasurement.DoesNotExist:
                pass
            except WellQualityMeasurement.DoesNotExist:
                pass

    def run(self):
        """Run the process."""
        from gwml2.signals.well import (
            post_delete_measurement_trigger_well_update
        )
        from gwml2.utilities import temp_disconnect_signal
        with temp_disconnect_signal(
                signal=post_delete,
                receiver=post_delete_measurement_trigger_well_update,
                sender=WellLevelMeasurement
        ):
            with temp_disconnect_signal(
                    signal=post_delete,
                    receiver=post_delete_measurement_trigger_well_update,
                    sender=WellYieldMeasurement
            ):
                with temp_disconnect_signal(
                        signal=post_delete,
                        receiver=post_delete_measurement_trigger_well_update,
                        sender=WellQualityMeasurement
                ):
                    try:
                        count = len(self.ids)
                        for idx, id in enumerate(self.ids):
                            logger.debug(f'{idx}/{count}')
                            try:
                                well = Well.objects.get(id=id)
                                title = f'{id}/{well.name}'
                                self.update_note(
                                    f'Deleting : {title}'
                                )

                                # Level measurements
                                self.delete_measurement(
                                    well.welllevelmeasurement_set,
                                    title=title
                                )
                                self.delete_measurement(
                                    well.wellyieldmeasurement_set,
                                    title=title
                                )
                                self.delete_measurement(
                                    well.wellqualitymeasurement_set,
                                    title=title
                                )
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
                        self.update_note(f'{e}')
                        logger.debug(f'{e}')
