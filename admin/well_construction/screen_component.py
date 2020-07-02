from django.contrib import admin
from gwml2.models.well_construction.screen_component import (
    AttachmentMethodTerm, ScreenCoatingTerm, ScreenFormTerm,
    ScreenMaterialTerm, PerforationMethodTerm,
    ScreenFittingTerm, ScreenMakerTerm,
    ScreenModelTerm, ScreenNumberTerm, ScreenPlacementTerm, ScreenComponent
)


class Admin(admin.ModelAdmin):
    list_display = ('screen_attachment_method', 'screen_coating', 'screen_form', 'screen_hole_size', 'construction_component')


admin.site.register(AttachmentMethodTerm)
admin.site.register(ScreenCoatingTerm)
admin.site.register(ScreenFormTerm)
admin.site.register(ScreenMaterialTerm)
admin.site.register(PerforationMethodTerm)
admin.site.register(ScreenFittingTerm)
admin.site.register(ScreenMakerTerm)
admin.site.register(ScreenModelTerm)
admin.site.register(ScreenNumberTerm)
admin.site.register(ScreenPlacementTerm)
admin.site.register(ScreenComponent, Admin)
