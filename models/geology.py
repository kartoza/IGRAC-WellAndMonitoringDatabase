from django.contrib.gis.db import models
from gwml2.models.general import Quantity


class Geology(models.Model):
    """ Geology model
    """
    total_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Total depth of geology'
    )


class GeologyLog(models.Model):
    """
    8.1.9 GW_GeologyLog
    Specialization of the OM_Observation containing the log start and end depth for
    coverages.
    For Stratigraphic logs the observedProperty will be a GeoSciML:GeologicUnit/name.
    For Lithologic logs the observedProperty will be a
    GeoSciML:GeologicUnit/composition/CompositionPart/material.
    """
    geology = models.ForeignKey(
        Geology, on_delete=models.CASCADE,
    )

    # Log information
    top_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Top depth of the log',
        related_name='geology_log_top_depth'
    )
    bottom_depth = models.ForeignKey(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Bottom depth of the log',
        related_name='geology_log_bottom_depth'
    )
    material = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="Material of the log."
    )
    geological_unit = models.CharField(
        null=True, blank=True, max_length=256,
        help_text="Geological unit of the log."
    )
