from django.contrib.gis.db import models
from gwml2.models.universal import GWTerm, Quantity
from gwml2.models.contact_information import CIResponsibleParty
from gwml2.models.geometry import GMEnvelope


class BoreholeDrillingMethodTerm(GWTerm):
    """
    Method of drilling.
    """
    pass


class BoreholeInclinationTerm(GWTerm):
    """
    Type of borehole inclination, e.g. vertical or horizontal.
    """
    pass


class BholeStartPointTypeTerm(GWTerm):
    """
    Describes the location of the start of the
    borehole, e.g. ground surface.
    """
    pass


class Borehole(models.Model):
    """
    8.1.2 Borehole
    General term for a hole drilled in the ground for various purposes such extraction of a
    core, release of fluid, etc.
    """
    name = models.TextField(
        null=True, blank=True,
        verbose_name="Name")
    bhole_material_custodian = models.ManyToManyField(
        CIResponsibleParty, null=True, blank=True,
        verbose_name="bholeMaterialCustodian",
        related_name='bhole_material_custodian',
        help_text="The custodian of the drill core or samples recovered from the borehole.")
    bhole_core_interval = models.ForeignKey(
        GMEnvelope, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeCoreInterval",
        help_text="The geometries for the intervals from which core"
                  "is extracted along the borehole.")
    bhole_date_of_drilling = models.DateField(
        null=True,
        verbose_name="bholeDateOfDrilling",
        help_text="Date of drilling.")
    bhole_driller = models.ForeignKey(
        CIResponsibleParty, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='bhole_driller',
        verbose_name="bholeDriller",
        help_text="The organisation responsible for drilling the "
                  "borehole (as opposed to commissioning the borehole).")
    bhole_drilling_method = models.ManyToManyField(
        BoreholeDrillingMethodTerm, null=True, blank=True,
        verbose_name="bholeDrillingMethod",
        help_text="Method of drilling.")
    bhole_inclination_type = models.ForeignKey(
        BoreholeInclinationTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeInclinationType",
        help_text="Type of borehole inclination, e.g. vertical or horizontal.")
    bhole_nominal_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeNominalDiameter",
        help_text="Diameter of the borehole.")
    bhole_operator = models.ForeignKey(
        CIResponsibleParty, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeOperator",
        related_name='bhole_operator',
        help_text="Organisation responsible for commissioning the"
                  "borehole (as opposed to drilling the borehole).")
    bhole_start_point = models.ForeignKey(
        BholeStartPointTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="bholeStartPoint",
        help_text="Describes the location of the start of the"
                  "borehole, e.g. ground surface.")

    def __str__(self):
        return self.name
