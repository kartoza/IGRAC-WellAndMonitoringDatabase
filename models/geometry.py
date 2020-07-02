from django.contrib.gis.db import models


class GMEnvelope(models.Model):
    """
   The geometries with upper and lower.
    """
    upper_corner = models.PointField(
        null=True, blank=True, verbose_name="UpperCorner",
        help_text="A coordinate consisting of all maximal values of the ordinates of all points within the GM_Envelope.",
        dim=3
    )
    lower_corner = models.PointField(
        null=True, blank=True, verbose_name="LowerCorner",
        help_text="A coordinate consisting of all minimal values of the ordinates of all points within the GM_Envelope.",
        dim=3
    )
