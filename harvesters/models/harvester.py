from django.contrib.gis.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from gwml2.models.term import TermFeatureType
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation


class Harvester(models.Model):
    """ Harvester of gwml2 data
    """
    harvester_class = models.CharField(
        max_length=100,
        unique=True,
        help_text=_(
            "The type of harvester that will be used."
            "Use class with full package.")
    )
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
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
        help_text=_('Default indicator for : well can be viewed by '
                    'non organisation user.')
    )
    downloadable = models.BooleanField(
        default=True,
        help_text=_('Default indicator : well can be downloaded.')
    )

    class Meta:
        db_table = 'harvester'

    def __str__(self):
        return self.harvester_class

    @property
    def get_harvester_class(self):
        return import_string(self.harvester_class)

    def run(self, replace=False, original_id=None):
        """ Run the harvester if active
        """
        if self.active and self.organisation:
            self.get_harvester_class(self, replace, original_id)

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


class HarvesterWellData(models.Model):
    """
    Well of data that is harvested
    This indicate the times of measurements that already harvested
    This time used for the next harvesting
    """
    harvester = models.ForeignKey(
        Harvester, on_delete=models.CASCADE
    )
    well = models.OneToOneField(
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
