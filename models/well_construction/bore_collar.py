from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm
from gwml2.models.well_construction.borehole import Borehole


class CollarElevationTypeTerm(GWTerm):
    """
    Type of reference elevation, defined as a feature,
    e.g. Top of Casing, Ground, etc.
    """
    pass


class HeadworkTypeTerm(GWTerm):
    """
    Type of assembly bolted to the production casing
    to control the well, and to provide access and
    protection (e.g. from flooding, vandalism).
    Example: raised tube, covers, manhole, 'Gattick
    Cover' flush, concrete ring, etc. (after Fretwell,
    et al., 2006).
    """
    pass


class BoreCollar(models.Model):
    """
    8.1.1 BoreCollar
    Topmost component of a borehole construction.
    """
    bhole_headworks = models.ForeignKey(
        Borehole,
        on_delete=models.CASCADE, verbose_name='bholeHeadworks',
        help_text="Relation between a borehole and its collar, "
                  "which represents the top construction component of the borehole.")

    collar_location = models.PointField(
        null=True, blank=True, verbose_name="collarLocation",
        help_text="The geographical location of the collar.",
        dim=3
    )
    collar_elevation_type = models.ForeignKey(
        CollarElevationTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='collarElevationType',
        help_text="Type of reference elevation, defined as a feature,"
                  "e.g. Top of Casing, Ground, etc.")
    collar_headwork_type = models.ForeignKey(
        HeadworkTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='collarHeadworkType',
        help_text="Type of assembly bolted to the production casing"
                  "to control the well, and to provide access and"
                  "protection (e.g. from flooding, vandalism)."
                  "Example: raised tube, covers, manhole, 'Gattick"
                  "Cover' flush, concrete ring, etc. (after Fretwell,"
                  "et al., 2006).")
    # TODO:
    #  Not sure about this, why needs manytomany
    # collar_elevation = models.PointField(
    #     null=True, blank=True, verbose_name="collarElevation",
    #     help_text="The elevation of the bore collar with CRS and UOM.",
    #     dim=3
    # )
