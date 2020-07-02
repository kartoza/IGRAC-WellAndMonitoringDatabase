from django.contrib.gis.db import models


class OMProcess(models.Model):
    """
    OM_Process describes observation methods or the
    calculation of aquifer parameters
    """
    name = models.CharField(max_length=512)
    description = models.TextField()

    def __str__(self):
        return self.name
