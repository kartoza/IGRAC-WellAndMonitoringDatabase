import os
from datetime import datetime

from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from gwml2.models.well import Well, MEASUREMENT_MODELS


class WellCacheIndicator(models.Model):
    """The well cache indicator model.

    It contains all cache indicator.
    """
    well = models.OneToOneField(Well, on_delete=models.CASCADE)

    # ----------------------------------------
    # Well cache indicator
    # ----------------------------------------
    measurement_cache_generated_at = models.DateTimeField(
        _('Time when measurement cache generated'),
        null=True, blank=True
    )
    data_cache_generated_at = models.DateTimeField(
        _('Time when data cache generated'),
        null=True, blank=True
    )
    metadata_generated_at = models.DateTimeField(
        _('Time when metadata generated'),
        null=True, blank=True
    )
    data_cache_information = models.JSONField(
        help_text=_(
            'Information about the data cache, '
            'like the time of file is being generated.'
        ),
        null=True, blank=True
    )

    def measurement_cache_generated_at_check(self, model):
        """Generate measurement cache at check."""
        _time = None
        well = self.well
        cache_file = well.return_measurement_cache_path(model)
        if os.path.exists(cache_file):
            modified_timestamp = os.path.getmtime(cache_file)
            modified_datetime = make_aware(
                datetime.fromtimestamp(modified_timestamp)
            )
            if (
                    not self.measurement_cache_generated_at or
                    modified_datetime > self.measurement_cache_generated_at
            ):
                _time = modified_datetime
        if _time:
            self.measurement_cache_generated_at = _time
            self.save()

    def generate_data_wells_cache(self, force=False, generators=None):
        """Generate data wells cache."""
        from gwml2.tasks.data_file_cache.wells_cache import (
            generate_data_well_cache
        )

        # Format generators
        if isinstance(generators, str):
            generators = generators.split(',')
        elif generators is None:
            generators = None

        generate_data_well_cache(
            self.well.id,
            force_regenerate=force,
            generate_country_cache=False,
            generate_organisation_cache=False,
            generators=generators
        )

    def generate_measurement_cache(self, measurement_name=None, force=False):
        """Generate measurement cache."""
        self.well.generate_all_measurement_caches(
            measurement_name=measurement_name,
            force=force
        )

    def generate_metadata(self, force=False):
        """Generate measurement cache."""
        if force and self.metadata_generated_at:
            return
        self.well.update_metadata()

    def run(self, force=False):
        """Force run cache."""
        self.generate_data_wells_cache(force=force)
        self.generate_measurement_cache(force=force)
        self.generate_metadata(force=force)

    def assign_data_cache_information(self):
        """Assign data cache information.
        We not use this on generator, just on the django admin command.
        """
        well = self.well
        self.data_cache_information = None
        self.save()
        self.data_cache_information = {}
        if os.path.exists(well.data_cache_folder):
            for root, dirs, files in os.walk(well.data_cache_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    modified_time = os.path.getmtime(file_path)
                    readable_time = datetime.fromtimestamp(modified_time)
                    self.data_cache_information[file] = (
                        readable_time.strftime('%Y-%m-%d %H:%M:%S')
                    )
        for MeasurementModel in MEASUREMENT_MODELS:
            measurement_name = MeasurementModel.__name__
            file_path = well.return_measurement_cache_path(measurement_name)
            if os.path.exists(file_path):
                file = os.path.basename(file_path).split('-')[1]
                modified_time = os.path.getmtime(file_path)
                readable_time = datetime.fromtimestamp(modified_time)
                self.data_cache_information[file] = (
                    readable_time.strftime('%Y-%m-%d %H:%M:%S')
                )
        self.save()


@receiver(post_save, sender=Well)
def update_well(sender, instance, created, **kwargs):
    """Create quality control when a well is created."""
    if created:
        WellCacheIndicator.objects.get_or_create(well=instance)
