from django.contrib.gis.db import models
from gwml2.models.general import Quantity, Country
from gwml2.models.term import TermFeatureType
from django.utils.translation import ugettext_lazy as _


class GeneralInformation(models.Model):
    """ Abstract model for General Information """
    original_id = models.CharField(
        _("Original ID"),
        max_length=512, help_text=_('As recorded in the original database.'))

    # geometry information
    location = models.PointField(
        _("Location"),
        help_text=_("Location of the feature.")
    )
    ground_surface_elevation = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text=_('Ground surface elevation above sea level.'),
        related_name='ground_surface_elevation',
        verbose_name=_('Ground surface elevation')
    )
    top_borehole_elevation = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text=_('Elevation of top of borehole above sea level.'),
        related_name='top_borehole_elevation',
        verbose_name=_('Top of well elevation')
    )

    name = models.CharField(
        _("Name"),
        null=True, blank=True, max_length=512
    )
    feature_type = models.ForeignKey(
        TermFeatureType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Feature type')
    )

    # location information
    address = models.TextField(
        _("Address"),
        null=True, blank=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Country')
    )

    # information
    photo = models.FileField(
        _("Photo"),
        null=True, blank=True,
        upload_to='gwml2/photos/',
        help_text=_('A photo of the groundwater point. More photos can be added in annex.')
    )
    description = models.TextField(
        _("Description"),
        null=True, blank=True,
        help_text=_('A general description of the groundwater point.')
    )

    class Meta:
        abstract = True
