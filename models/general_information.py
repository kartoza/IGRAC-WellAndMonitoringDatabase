from django.contrib.gis.db import models
from gwml2.models.general import Quantity, Country
from gwml2.models.term import TermFeatureType


class GeneralInformation(models.Model):
    """ Abstract model for General Information """
    name = models.CharField(
        null=True, blank=True, max_length=512,
        help_text="Name of information."
    )
    feature_type = models.ForeignKey(
        TermFeatureType, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Type of the feature."
    )

    # geometry information
    location = models.PointField(
        verbose_name="location",
        help_text="Location of the feature."
    )
    elevation = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Elevation of the feature."
    )

    # location information
    address = models.TextField(
        null=True, blank=True,
        help_text="Address of the feature."
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Country of the feature."
    )

    # information
    photo = models.FileField(
        null=True, blank=True,
        upload_to='gwml2/photos/'
    )
    description = models.TextField(
        null=True, blank=True,
        help_text="Description of the feature."
    )

    class Meta:
        abstract = True
