from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from gwml2.models.general import Quantity
from gwml2.models.term import TermAquiferType, TermConfinement


class PumpingTest(models.Model):
    """ Model for Pumping Test
    """
    # pumping test information
    porosity = models.FloatField(
        _('Porosity'),
        null=True, blank=True
    )
    specific_capacity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_specific_capacity',
        help_text=_('Specific capacity is the pumping rate divided by the drawdown. It gives an indication of the yield of a well.'),
        verbose_name=_('Specific capacity')
    )
    hydraulic_conductivity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_hydraulic_conductivity',
        verbose_name=_('Hydraulic conductivity')
    )
    transmissivity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_transmissivity',
        help_text=_('Transmissivity is the hydraulic conductivity integrated over the thickness of the aquifer.'),
        verbose_name=_('Transmissivity')
    )
    specific_storage = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_specific_storage',
        verbose_name=_('Specific storage')
    )
    specific_yield = models.FloatField(
        _('Specific yield'),
        null=True, blank=True
    )
    storativity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_storativity',
        verbose_name=_('Yield')
    )
    test_type = models.CharField(
        _('Test type'),
        null=True, blank=True, max_length=512,
        help_text=_('Provide information on the test(s) performed to estimate the hydraulic properties.')
    )

    class Meta:
        db_table = 'pumping_test'


class HydrogeologyParameter(models.Model):
    """ Model for hydrogeology parameter
    """

    aquifer_name = models.CharField(
        _('Aquifer name'),
        null=True, blank=True, max_length=512
    )
    aquifer_material = models.CharField(
        _('Aquifer material'),
        null=True, blank=True, max_length=512
    )
    aquifer_type = models.ForeignKey(
        TermAquiferType, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Aquifer type')
    )
    aquifer_thickness = models.CharField(
        _('Aquifer thickness'),
        null=True, blank=True, max_length=512
    )
    confinement = models.ForeignKey(
        TermConfinement, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Confinement')
    )
    degree_of_confinement = models.FloatField(
        _('Degree of confinement'),
        null=True, blank=True
    )
    pumping_test = models.OneToOneField(
        PumpingTest, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        db_table = 'hydrogeology_parameter'
