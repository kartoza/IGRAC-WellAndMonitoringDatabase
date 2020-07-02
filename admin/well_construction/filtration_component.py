from django.contrib import admin
from gwml2.models.well_construction.filtration_component import (
    FiltrationMaterialTerm, FiltrationComponent
)


class Admin(admin.ModelAdmin):
    list_display = ('filter_grain_size', 'filter_material', 'construction_component')


admin.site.register(FiltrationMaterialTerm)
admin.site.register(FiltrationComponent, Admin)
