from django.contrib import admin
from gwml2.models.well_construction.bore_collar import BoreCollar
from gwml2.models.well_construction.borehole import (
    Borehole, BoreholeDrillingMethodTerm, BoreholeInclinationTerm,
    BholeStartPointTypeTerm
)


class BoreCollarInline(admin.TabularInline):
    model = BoreCollar


class Admin(admin.ModelAdmin):
    filter_horizontal = ('installed_equipment', 'bhole_material_custodian', 'bhole_drilling_method')
    inlines = [BoreCollarInline, ]


admin.site.register(BoreholeDrillingMethodTerm)
admin.site.register(BoreholeInclinationTerm)
admin.site.register(BholeStartPointTypeTerm)
admin.site.register(Borehole, Admin)
