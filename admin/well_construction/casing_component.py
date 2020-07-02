from django.contrib import admin
from gwml2.models.well_construction.casing_component import (
    CasingMaterialTerm, CasingCoatingTerm, CasingFormTerm, CasingComponent
)


class Admin(admin.ModelAdmin):
    list_display = ('casing_material', 'casing_coating', 'casing_form',
                    'casing_internal_diameter', 'casing_external_diameter',
                    'casing_wall_thickness')


admin.site.register(CasingMaterialTerm)
admin.site.register(CasingCoatingTerm)
admin.site.register(CasingFormTerm)
admin.site.register(CasingComponent, Admin)
