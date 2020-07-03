from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm


class SpatialConfinementTypeTerm(GWTerm):
    """
    Degree of spatial confinement (typically:
    "Unconfined-Confined", "Partially Confined").
    """
    pass


class ConductivityConfinementTypeTerm(GWTerm):
    """
    Degree of hydraulic confinement (e.g. aquiclude).
    """
    pass


class GWConfiningBed(models.Model):
    """
    7.6.11 GW_ConfiningBed
    A layer of rock having very low porosity and in consequence hydraulic conductivity that
    hampers the movement of water into and out of an aquifer (Heath, 1983).
    """
    gw_spatial_confinement = models.ForeignKey(
        SpatialConfinementTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="gwSpatialConfinement",
        help_text="Degree of hydraulic confinement (e.g. aquiclude)."
    )

    gw_conductivity_confinement = models.ForeignKey(
        ConductivityConfinementTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="GWConductivityConfinement",
        help_text="Degree of spatial confinement (typically:"
                  "\"Unconfined-Confined\", \"Partially Confined\")."
    )
