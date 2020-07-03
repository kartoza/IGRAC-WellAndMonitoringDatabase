from django.contrib import admin
from gwml2.models.gw_management_area import (
    ManagementAreaTypeTerm, SpecialisedZoneAreaTypeTerm,
    EnvironmentalDomainTypeTerm, GWManagementArea)


class Admin(admin.ModelAdmin):
    filter_horizontal = ('gw_area_water_budget', 'gw_area_competent_authority',
                         'gw_area_body', 'gw_managed_unit')


admin.site.register(ManagementAreaTypeTerm)
admin.site.register(SpecialisedZoneAreaTypeTerm)
admin.site.register(EnvironmentalDomainTypeTerm)
admin.site.register(GWManagementArea, Admin)
