from django.contrib.gis.db import models
from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.drilling import Drilling
from gwml2.models.construction import Construction
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.term import TermWellPurpose
from gwml2.models.reference_elevation import ReferenceElevation


# Monitoring data
class WellGroundwaterLevel(models.Model):
    """ Groundwater level of well"""
    reference_elevation = models.OneToOneField(
        ReferenceElevation, on_delete=models.SET_NULL,
        null=True, blank=True
    )


class WellGroundwaterLevelMeasurement(Measurement):
    groundwater_level = models.ForeignKey(
        WellGroundwaterLevel, on_delete=models.CASCADE,
    )


class Well(GeneralInformation):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""
    original_id = models.CharField(
        unique=True, max_length=256)
    purpose = models.ForeignKey(
        TermWellPurpose, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    drilling = models.OneToOneField(
        Drilling, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    construction = models.OneToOneField(
        Construction, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    management = models.OneToOneField(
        Management, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    hydrogeology_parameter = models.OneToOneField(
        HydrogeologyParameter, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    groundwater_level = models.OneToOneField(
        WellGroundwaterLevel, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.original_id

    class Meta:
        ordering = ['original_id']


# documents
class WellDocument(Document):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )


# Monitoring data
class WellQualityMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )


class WellYieldMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )
