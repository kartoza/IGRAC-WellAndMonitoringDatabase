from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm
from gwml2.models.fluid_body.gw_constituent import GWConstituent


class MixtureType(GWTerm):
    """
    The manner in which a constituent is within a fluid body,
    e.g. solution, suspension, emulsion, precipitate, colloidal.

    """

    pass


class GWMixture(models.Model):
    """
    7.6.28 GW_Mixture
    The nature of the inclusion of the constituent in the fluid body, e.g. suspension, emulsion, etc.

    """

    gw_mixture = models.ForeignKey(
        MixtureType, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='gwMixture',
        help_text="The manner in which a constituent is within a fluid body, "
                  "e.g. solution, suspension, emulsion, precipitate, colloidal.")

    def __str__(self):
        return self.gw_mixture


class GWMixtureConstituent(models.Model):
    """
    The model that connect GW_Mixture and GW_Constituent.

    """

    gw_mixture = models.ForeignKey(
        GWMixture, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='GW_Mixture')
    gw_constituent = models.ForeignKey(
        GWConstituent, null=False, blank=False,
        on_delete=models.CASCADE, verbose_name='GW_Constituent')

    def __str__(self):
        return '{} - {}'.format(self.gw_mixture, self.gw_constituent)
