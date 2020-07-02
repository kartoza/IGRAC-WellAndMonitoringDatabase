from django.contrib.gis.db import models
from gwml2.models.universal import Quantity, GWTerm
from gwml2.models.well_construction import ConstructionComponent


class AttachmentMethodTerm(GWTerm):
    """
    Screen attachment method. E.g. telescoped, on
    casing, on riser pipe, neoprene (K) packer, Lead packer, etc.
    """
    pass


class ScreenCoatingTerm(GWTerm):
    """
    Thin outer layer applied to the screen. E.g.
    galvanized, stainless, copper bearing, low
    carbon, black, porous, etc.
    """
    pass


class ScreenFormTerm(GWTerm):
    """
    Form of the screen. E.g. slotted casing,
    perforated casing, bridge slot casing, wire wrap
    or continuous slot, wire mesh, shutter or
    louvered, well point, tube, etc.
    """
    pass


class ScreenMaterialTerm(GWTerm):
    """
    Material that makes up the screen. E.g. metal,
    steel, iron, copper, brass, bronze, everdur,
    Armco metal, veriperm, stone, plastic, PVC,
    ABS, Fibreglass, etc.
    """
    pass


class PerforationMethodTerm(GWTerm):
    """
    Method used for perforating the screen. E.g.
    drill, grinder, axe / chisel, machine, saw, torch,
    other, etc.
    """
    pass


class ScreenFittingTerm(GWTerm):
    """
    The screen fitting (from the bottom). E.g. bail,
    open, plug, tail pipe, washdown, etc.
    """
    pass


class ScreenMakerTerm(GWTerm):
    """
    Make of the screen.
    """
    pass


class ScreenModelTerm(GWTerm):
    """
    Model of the screen.
    """
    pass


class ScreenNumberTerm(GWTerm):
    """
    Screen number corresponds to hole size and is
    given in 0.001 inch. The value is expressed as an
    alphanumeric code.
    """
    pass


class ScreenPlacementTerm(GWTerm):
    """
    Screen placement method. E.g. bail down, pull
    back, jetted, washed down, etc.
    """
    pass


class ScreenComponent(models.Model):
    """
    8.1.13 ScreenComponent
    Component of the well lining where water enters the well.
    """

    screen_attachment_method = models.ForeignKey(
        AttachmentMethodTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenAttachmentMethod',
        help_text="Screen attachment method. E.g. telescoped, on"
                  "casing, on riser pipe, neoprene (K) packer, Lead packer, etc.")

    screen_coating = models.ForeignKey(
        ScreenCoatingTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenCoating',
        help_text="Thin outer layer applied to the screen. E.g."
                  "galvanized, stainless, copper bearing, "
                  "low carbon, black, porous, etc.")

    screen_form = models.ForeignKey(
        ScreenFormTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenForm',
        help_text="Form of the screen. E.g. slotted casing,"
                  "perforated casing, bridge slot casing, wire wrap"
                  "or continuous slot, wire mesh, shutter or"
                  "louvered, well point, tube, etc.")

    screen_hole_size = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='screen_hole_size',
        on_delete=models.SET_NULL, verbose_name='screenHoleSize',
        help_text="Size of the slots or perforations of the screen.")

    screen_material = models.ForeignKey(
        ScreenMaterialTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenMaterial',
        help_text="Material that makes up the screen. E.g. metal,"
                  "steel, iron, copper, brass, bronze, everdur,"
                  "Armco metal, veriperm, stone, plastic, PVC,"
                  "ABS, Fibreglass, etc.")

    screen_internal_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='screen_internal_diameter',
        on_delete=models.SET_NULL, verbose_name='screenInternalDiameter',
        help_text="Internal screen diameter.")

    screen_external_diameter = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='screen_external_diameter',
        on_delete=models.SET_NULL, verbose_name='screenExternalDiameter',
        help_text="External screen diameter.")

    screen_perforation_method = models.ForeignKey(
        PerforationMethodTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenPerforationMethod',
        help_text="Method used for perforating the screen. E.g."
                  "drill, grinder, axe / chisel, machine, saw, torch,"
                  "other, etc.")

    screen_fitting = models.ForeignKey(
        ScreenFittingTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenFitting',
        help_text="The screen fitting (from the bottom). E.g. bail,"
                  "open, plug, tail pipe, washdown, etc.")

    screen_make = models.ForeignKey(
        ScreenMakerTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenMake',
        help_text="Make of the screen.")

    screen_model = models.ForeignKey(
        ScreenModelTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenModel',
        help_text="Model of the screen.")

    screen_number = models.ForeignKey(
        ScreenNumberTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenNumber',
        help_text="Screen number corresponds to hole size and is"
                  "given in 0.001 inch. The value is expressed "
                  "as an alphanumeric code.")

    screen_placement = models.ForeignKey(
        ScreenPlacementTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='screenPlacement',
        help_text="Screen placement method. E.g. bail down, pull"
                  "back, jetted, washed down, etc.")

    screen_wall_thickness = models.OneToOneField(
        Quantity, null=True, blank=True,
        related_name='screen_wall_thickness',
        on_delete=models.SET_NULL, verbose_name='screenWallThickness',
        help_text="Thickness of the screen wall.")

    # TODO:
    #   need to ask about this construction component is
    #   just 1 for a screen or many?
    construction_component = models.ForeignKey(
        ConstructionComponent, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="ConstructionComponent",
        help_text="A screen part is a type of construction component.")
