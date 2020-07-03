from django.contrib.gis.db import models
from gwml2.models.flow.gw_divide import GWDivide


class GWBasin(models.Model):
    """
    7.6.8 GW_Basin
    A large hydrogeologically defined body of ground typically consisting of hydraulically
    connected hydrogeological units, whose waters are flowing to a common or multiple
    outlets, and which is delimited by a groundwater divide.
    """

    gw_divide = models.ManyToManyField(
        GWDivide,
        verbose_name="GWDivide",
        help_text="“Line on a water table or piezometric surface on "
                  "either side of which the groundwater flow diverges“ (IGH0556)."
    )
