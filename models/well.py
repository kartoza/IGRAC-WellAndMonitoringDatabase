from django.contrib.gis.db import models
from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.drilling import Drilling
from gwml2.models.construction import Construction
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.term import TermWellPurpose, TermWellStatus


class Well(GeneralInformation):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""
    original_id = models.CharField(
        unique=True, max_length=256,
        help_text='As recorded in the original database.')
    purpose = models.ForeignKey(
        TermWellPurpose, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    status = models.ForeignKey(
        TermWellStatus, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    drilling = models.OneToOneField(
        Drilling, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    geology = models.OneToOneField(
        Geology, on_delete=models.SET_NULL,
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

    def __str__(self):
        return self.original_id

    class Meta:
        db_table = 'well'
        ordering = ['original_id']

    def relation_queryset(self, relation_model_name):
        """ Return queryset of relation of model
        """
        if relation_model_name == 'WellDocument':
            return self.welldocument_set
        elif relation_model_name == 'WaterStrike':
            return self.drilling.waterstrike_set
        elif relation_model_name == 'StratigraphicLog':
            return self.drilling.stratigraphiclog_set
        elif relation_model_name == 'ConstructionStructure':
            return self.construction.constructionstructure_set
        elif relation_model_name == 'WellLevelMeasurement':
            return self.welllevelmeasurement_set
        elif relation_model_name == 'WellQualityMeasurement':
            return self.wellqualitymeasurement_set
        elif relation_model_name == 'WellYieldMeasurement':
            return self.wellyieldmeasurement_set
        return None


# documents
class WellDocument(Document):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_document'


# Monitoring data
class WellLevelMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_level_measurement'
        ordering = ('-time',)


class WellQualityMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_quality_measurement'
        ordering = ('-time',)


class WellYieldMeasurement(Measurement):
    well = models.ForeignKey(
        Well, on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'well_yield_measurement'
        ordering = ('-time',)
