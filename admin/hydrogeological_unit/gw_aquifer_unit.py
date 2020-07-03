from django.contrib import admin
from gwml2.models.hydrogeological_unit.gw_aquifer_unit import GWAquiferUnit


class Admin(admin.ModelAdmin):
    filter_horizontal = ('gw_aquifer_system',)


admin.site.register(GWAquiferUnit, Admin)
