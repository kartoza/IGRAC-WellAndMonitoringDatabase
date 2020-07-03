from django.contrib.gis.db import models


class GWAquiferSystem(models.Model):
    """
    7.6.6 GW_AquiferSystem
    Aquifer system - a body of permeable and poorly permeable material that functions
    regionally as a water-yielding unit; it comprises two or more permeable beds separated at
    least locally by confining beds that impede groundwater movement but do not greatly
    affect the regional hydraulic continuity of the system; includes both saturated and
    unsaturated parts of permeable material (after ASCE, 1987).
    """

    gw_aquifer_system_is_layered = models.BooleanField(
        null=True, blank=True,
        verbose_name="gwAquiferSystemIsLayered",
        help_text="True if this aquifer / system is a layered system."
                  "(after INSPIRE, 2013)."
    )

    # TODO:
    #  On the graph, this model has relation with GW_ConfiningBed
    #  But no description on 7.6.6 GW_AquiferSystem or on GW_ConfiningBed itself
