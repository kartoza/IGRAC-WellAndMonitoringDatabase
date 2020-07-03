from django.contrib import admin
from gwml2.models.hydrogeological_unit.gw_basin import GWBasin


class Admin(admin.ModelAdmin):
    filter_horizontal = ('gw_divide',)


admin.site.register(GWBasin, Admin)
