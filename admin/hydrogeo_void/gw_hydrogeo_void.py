from django.contrib import admin
from gwml2.models.hydrogeo_void.gw_hydrogeo_void import *


class GWVoidUnitAdmin(admin.ModelAdmin):
    list_display = ('gw_hydrogeo_unit', 'gw_unit_void_property',)


admin.site.register(GWHydrogeoVoid)
admin.site.register(GWVoidUnit, GWVoidUnitAdmin)
