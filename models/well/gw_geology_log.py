from django.contrib.gis.db import models
from gwml2.models import Quantity
from gwml2.models.well import GWWell
from gwml2.models.observations_measurements import OMObservation
from gwml2.models.time import TMPeriod
from gwml2.models.universal import NamedValue


class GWGeologyLog(models.Model):
    """
    8.1.9 GW_GeologyLog
    Specialization of the OM_Observation containing the log start and end depth for
    coverages.
    For Stratigraphic logs the observedProperty will be a GeoSciML:GeologicUnit/name.
    For Lithologic logs the observedProperty will be a
    GeoSciML:GeologicUnit/composition/CompositionPart/material.
    """

    phenomenon_time = models.DateTimeField(
        null=True, blank=True, verbose_name='phenomenonTime',
        help_text='Reflects the time that the result applies to the property'
    )
    result_time = models.DateTimeField(
        null=True, blank=True, verbose_name='resultTime',
        help_text='The time at which the value has been obtained or became available'
    )
    valid_time = models.ForeignKey(
        TMPeriod, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='The time during which the value is usable.',
        verbose_name='validTime')
    resultQuality = models.TextField(
        null=True, blank=True, verbose_name='resultQuality',
        help_text='The quality of the result'
    )
    parameter = models.ManyToManyField(
        NamedValue, null=True, blank=True, verbose_name='parameter',
        help_text='This shall describe an arbitrary event-specific parameter. '
                  'This might be an environmental parameter, an instrument setting or input, '
                  'or an event-specific sampling parameter that is not tightly bound to either the feature-of-interest'
                  ' or to the observation procedure (6.2.2.10).'
    )
    gw_level = models.FloatField(
        null=True, blank=True, verbose_name='gw_level')
    reference = models.TextField(
        null=True, blank=True, verbose_name='reference')
    start_depth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='startDepth',
        verbose_name='startDepth')
    end_depth = models.ForeignKey(
        Quantity, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='endDepth',
        verbose_name='endDepth')
    gw_well = models.ForeignKey(
        GWWell,
        null=True, blank=True, verbose_name="gwWell",
        on_delete=models.SET_NULL)  # many to one to GWWell

    def __str__(self):
        return self.gw_well
