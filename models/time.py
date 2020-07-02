from django.contrib.gis.db import models


class TMPeriod(models.Model):
    """Time Period model."""

    start_time = models.DateTimeField(
        null=True, blank=True, verbose_name='startTime')
    end_time = models.DateTimeField(
        null=True, blank=True, verbose_name='endTime')

    def __str__(self):
        return '{} - {}'.format(self.start_time, self.end_time)
