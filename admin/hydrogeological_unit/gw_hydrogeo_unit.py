from django.contrib import admin
from gwml2.models.hydrogeological_unit.gw_hydrogeo_unit import GWHydrogeoUnit


class Admin(admin.ModelAdmin):
    filter_horizontal = ('gw_unit_recharge', 'gw_unit_discharge',
                         'gw_unit_vulnerability', 'properties')


admin.site.register(GWHydrogeoUnit, Admin)
