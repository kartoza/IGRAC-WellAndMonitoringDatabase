from django.contrib.gis.db import models
from gwml2.models.general import Quantity, Country
from gwml2.models.term import TermFeatureType


class GeneralInformation(models.Model):
    """ Abstract model for General Information """
    name = models.CharField(
        null=True, blank=True, max_length=512
    )
    feature_type = models.ForeignKey(
        TermFeatureType, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # geometry information
    location = models.PointField(
        verbose_name="location",
        help_text="Location of the feature."
    )
    ground_surface_elevation = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Ground Surface Elevation Above Sea Level.',
        related_name='ground_surface_elevation'
    )
    top_borehole_elevation = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Elevation of Top of Borehole Above Sea Level.',
        related_name='top_borehole_elevation'
    )

    # location information
    address = models.TextField(
        null=True, blank=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # information
    photo = models.FileField(
        null=True, blank=True,
        upload_to='gwml2/photos/',
        help_text='A photo of the groundwater point. More photos can be added in annex. '
    )
    description = models.TextField(
        null=True, blank=True,
        help_text='A general description of the groundwater point.'
    )

    class Meta:
        abstract = True
