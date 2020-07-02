from django.contrib import admin
from gwml2.models.well_construction.sealing_component import (
    SealingTypeTerm,
    SealingMaterialTerm,
    SealingComponent
)


class Admin(admin.ModelAdmin):
    list_display = ('sealing_material', 'sealing_type')


admin.site.register(SealingTypeTerm)
admin.site.register(SealingMaterialTerm)
admin.site.register(SealingComponent, Admin)
