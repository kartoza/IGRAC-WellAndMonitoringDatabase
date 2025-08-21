import os
from datetime import datetime

from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from gwml2.models.well import Well


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
        generate_data_well_cache(
            self.well.id,
            force_regenerate=force,
            generate_country_cache=False,
            generate_organisation_cache=False,
            generators=generators.split(',') if generators else None
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


@receiver(post_save, sender=Well)
def update_well(sender, instance, created, **kwargs):
    """Create quality control when a well is created."""
    if created:
        WellCacheIndicator.objects.get_or_create(well=instance)
