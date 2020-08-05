from django.contrib.gis.db import models
from gwml2.models.document import Document
from gwml2.models.general_information import GeneralInformation
from gwml2.models.geology import Geology
from gwml2.models.drilling_and_construction import DrillingAndConstruction
from gwml2.models.measurement import Measurement
from gwml2.models.management import Management
from gwml2.models.hydrogeology import HydrogeologyParameter


class Spring(GeneralInformation):
    """
    7.6.32 GW_Spring
    Any natural feature where groundwater flows to the surface of the earth.
    """
    geology = models.ForeignKey(
        Geology, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    drilling_and_construction = models.ForeignKey(
        DrillingAndConstruction, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    management = models.ForeignKey(
        Management, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    hydrogeology_parameter = models.ForeignKey(
        HydrogeologyParameter, on_delete=models.SET_NULL,
        null=True, blank=True
    )


class SpringMeasurement(Measurement):
    spring = models.ForeignKey(
        Spring, on_delete=models.CASCADE,
    )


class SpringDocument(Document):
    spring = models.ForeignKey(
        Spring, on_delete=models.CASCADE,
    )
