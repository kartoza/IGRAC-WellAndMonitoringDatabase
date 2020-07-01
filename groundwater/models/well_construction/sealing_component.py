from django.contrib.gis.db import models
from groundwater.models import GWTerm


class SealingTypeTerm(GWTerm):
    """
    Type of sealing. E.g. annular sealing, plugging, etc.
    """
    pass


class SealingMaterialTerm(GWTerm):
    """
    Material used in the sealing component of a
    water well. E.g. formation packer, welded ring,
    shale trap, drive shoe, driven casing, etc.
    """
    pass


class SealingComponent(models.Model):
    """
    8.1.15 SealingComponent
    A material used for sealing the construction of a borehole or well.
    """
    sealing_material = models.ForeignKey(
        SealingMaterialTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='sealingMaterial',
        help_text="Material used in the sealing component of a "
                  "water well. E.g. formation packer, welded ring, "
                  "shale trap, drive shoe, driven casing, etc.")
    sealing_type = models.ForeignKey(
        SealingTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='sealingType',
        help_text="Type of sealing. E.g. annular sealing, plugging, etc.")
