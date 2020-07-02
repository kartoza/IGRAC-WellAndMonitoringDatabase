from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm


class EquipmentCharacteristicTerm(GWTerm):
    """
    General characteristics of the equipment.
    """
    pass


class EquipmentTypeTerm(GWTerm):
    """
    Type of equipment.
    """
    pass


class Equipment(models.Model):
    """
    8.1.6 Equipment
    Equipment installed in a borehole (like a pump or any other device).
    """
    characteristics = models.ManyToManyField(
        EquipmentCharacteristicTerm, null=True, blank=True,
        verbose_name='Characteristics',
        help_text="General characteristics of the equipment.")
    equipment_type = models.ForeignKey(
        EquipmentTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='EquipmentType',
        help_text="Type of equipment.")
    installation_date = models.DateField(
        null=True,
        verbose_name="installationDate",
        help_text="Date of installation of the equipment.")
