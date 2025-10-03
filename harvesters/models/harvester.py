from datetime import timedelta

from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from gwml2.models import Unit
from gwml2.models.term import TermFeatureType
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.utils.celery import id_task_is_running


class Harvester(models.Model):
    """ Harvester of gwml2 data
    """
    harvester_class = models.CharField(
        max_length=100,
        help_text=_(
            "The type of harvester that will be used."
            "Use class with full package.")
    )
    name = models.CharField(
        _('Name'),
        max_length=100,
        help_text=_("Name of harvester that.")
    )
    description = models.TextField(
        blank=True, null=True
    )
    organisation = models.ForeignKey(
        Organisation,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        help_text=_(
            "Organisation for this harvester. "
            "It will be used as default of well's organisation")
    )
    feature_type = models.ForeignKey(
        TermFeatureType, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text=_(
            'Default feature type for the extracted wells.')
    )
    active = models.BooleanField(
        default=True,
        help_text=_(
            "Make this harvester ready to be harvested periodically.")
    )
    is_run = models.BooleanField(
        default=False,
        help_text=_("Is the harvester running.")
    )

    save_missing_well = models.BooleanField(
        default=False,
        help_text=_('Indicate that this harvester saves missing well.')
    )

    # TODO:
    #  We remove this after permissions has been merged
    public = models.BooleanField(
        default=True,
        help_text=_(
            'Default indicator for : well can be viewed by '
            'non organisation user.'
        )
    )
    downloadable = models.BooleanField(
        default=True,
        help_text=_('Default indicator : well can be downloaded.')
    )

    wagtail_reference_index_ignore = True

    task_id = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'harvester'
        unique_together = ('harvester_class', 'name')

    def __str__(self):
        return self.harvester_class

    @property
    def get_harvester_class(self):
        return import_string(self.harvester_class)

    def run(self, replace=False, original_id=None):
        """ Run the harvester if active."""
        try:
            if self.active and self.organisation:
                self.get_harvester_class(self, replace, original_id)
            elif not self.active:
                raise Exception('Harvester is not active')
            elif not self.organisation:
                raise Exception('Organisation is not setup')
        except Exception as e:
            self.task_id = None
            self.save()
            HarvesterLog.objects.create(
                harvester=self,
                status=ERROR,
                end_time=timezone.now(),
                note=f'{e}'
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        harvester = self.get_harvester_class
        for key, value in harvester.additional_attributes().items():
            HarvesterAttribute.objects.get_or_create(
                harvester=self,
                name=key,
                defaults={
                    'value': value
                }
            )

    @property
    def is_running_on_celery(self):
        """Is running on celery."""
        return id_task_is_running(self.task_id)

    @property
    def last_run(self):
        """Return last run."""
        last_log = self.harvesterlog_set.all().first()
        if not last_log:
            return None
        return last_log.start_time

    @property
    def is_actual_running(self):
        """Check if the harvester is actual running."""
        if not self.last_run:
            return False

        if not self.task_id:
            return False

        if timezone.now() - self.last_run <= timedelta(hours=4):
            return True

        return self.is_running_on_celery

    @staticmethod
    def return_running_harvesters():
        """Return running harvesters."""
        ids = []
        for obj in Harvester.objects.filter(active=True).all():
            if obj.is_actual_running:
                ids.append(obj.id)
            else:
                obj.reset()
        return Harvester.objects.filter(id__in=ids)

    def reset(self):
        """Reset harvester."""
        self.is_run = False
        self.harvesterlog_set.filter(status=RUNNING).update(
            status=ERROR, note='Worker stopped'
        )
        self.save()


class HarvesterAttribute(models.Model):
    """ Additional attribute for harvester"""
    harvester = models.ForeignKey(
        Harvester, on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=100,
        help_text=_(
            "The name of attribute")
    )
    value = models.TextField(
        null=True, default=True,
        help_text=_(
            "The value of attribute")
    )

    class Meta:
        db_table = 'harvester_attribute'
        unique_together = ('harvester', 'name')


class HarvesterParameterMap(models.Model):
    """Mapping parameters for harvester with igrac parameter and unit."""
    harvester = models.ForeignKey(
        Harvester, on_delete=models.CASCADE
    )
    key = models.CharField(
        max_length=512,
        help_text=_("The key on the api")
    )
    parameter = models.ForeignKey(
        TermMeasurementParameter, on_delete=models.CASCADE
    )
    unit = models.ForeignKey(
        Unit, null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'harvester_parameter_map'
        unique_together = ('harvester', 'key')
        ordering = ('key',)

    @staticmethod
    def get_json(harvester: Harvester) -> dict:
        """Return json of attribute."""
        return {
            obj.key: {
                "parameter": obj.parameter,
                "unit": obj.unit
            }
            for obj in harvester.harvesterparametermap_set.all()
        }


RUNNING = 'Running'
ERROR = 'Error'
DONE = 'Done'
STATUS = (
    (RUNNING, RUNNING),
    (DONE, DONE),
    (ERROR, ERROR),
)


class HarvesterLog(models.Model):
    """ History of harvester """
    harvester = models.ForeignKey(
        Harvester, on_delete=models.CASCADE
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        help_text=_(
            "This is when the harvester is started.")
    )
    end_time = models.DateTimeField(
        blank=True, null=True
    )
    status = models.CharField(
        max_length=100,
        choices=STATUS,
        default=RUNNING
    )
    note = models.TextField(
        blank=True, null=True
    )

    class Meta:
        db_table = 'harvester_log'
        ordering = ('-start_time',)


# TODO:
#  Clean this, as we can remove this needs
class HarvesterWellData(models.Model):
    """
    Well of data that is harvested
    This indicate the times of measurements that already harvested
    This time used for the next harvesting
    """
    harvester = models.ForeignKey(
        Harvester, on_delete=models.CASCADE
    )
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE
    )
    measurements_found = models.IntegerField(
        default=0,
        help_text=_(
            "Number of measurements found.")
    )
    from_time_data = models.DateTimeField(
        null=True, blank=True,
        help_text=_(
            "The time of oldest measurement that are harvested.")
    )
    to_time_data = models.DateTimeField(
        null=True, blank=True,
        help_text=_(
            "The time of newest measurement that are harvested.")
    )

    class Meta:
        db_table = 'harvester_well_data'
        verbose_name_plural = 'Harvester well data'
