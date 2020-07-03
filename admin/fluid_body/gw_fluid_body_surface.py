from django.contrib import admin
from gwml2.models.fluid_body.gw_fluid_body_surface import *


class GWFluidBodySurfaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'gw_surface_type')
    filter_horizontal = ('gw_surface_divide',)


admin.site.register(SurfaceType)
admin.site.register(GWFluidBodySurface, GWFluidBodySurfaceAdmin)
