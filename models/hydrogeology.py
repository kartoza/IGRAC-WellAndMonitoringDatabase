from django.contrib.gis.db import models
from gwml2.models.general import Quantity
from gwml2.models.term import TermAquiferType, TermConfinement


class PumpingTest(models.Model):
    """ Model for Pumping Test
    """
    # pumping test information
    porosity = models.FloatField(
        null=True, blank=True
    )
    specific_capacity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_specific_capacity',
        help_text='Specific capacity is the pumping rate divided by the drawdown. It gives an indication of the yield of a well.'
    )
    hydraulic_conductivity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_hydraulic_conductivity'
    )
    transmissivity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_transmissivity',
        help_text='Transmissivity is the hydraulic conductivity integrated over the thickness of the aquifer.'
    )
    specific_storage = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_specific_storage'
    )
    specific_yield = models.FloatField(
        null=True, blank=True
    )
    storativity = models.OneToOneField(
        Quantity, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pumping_test_storativity'
    )
    test_type = models.CharField(
        null=True, blank=True, max_length=512,
        help_text='Provide information on the test(s) performed to estimate the hydraulic properties.'
    )

    class Meta:
        db_table = 'pumping_test'


class HydrogeologyParameter(models.Model):
    """ Model for hydrogeology parameter
    """

    aquifer_name = models.CharField(
        null=True, blank=True, max_length=512
    )
    aquifer_material = models.CharField(
        null=True, blank=True, max_length=512
    )
    aquifer_type = models.ForeignKey(
        TermAquiferType, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    aquifer_thickness = models.CharField(
        null=True, blank=True, max_length=512
    )
    confinement = models.ForeignKey(
        TermConfinement, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    degree_of_confinement = models.FloatField(
        null=True, blank=True
    )
    pumping_test = models.OneToOneField(
        PumpingTest, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        db_table = 'hydrogeology_parameter'
