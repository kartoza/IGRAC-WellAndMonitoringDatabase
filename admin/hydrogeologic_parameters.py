from django.contrib import admin
from gwml2.models.hydrogeology import HydrogeologyParameter, PumpingTest


class PumpingTestAdmin(admin.ModelAdmin):
    list_display = (
        'test_type', 'porosity', 'hydraulic_conductivity',
        'transmissivity', 'specific_storage', 'storativity')


class HydrogeologyParameterAdmin(admin.ModelAdmin):
    list_display = ('aquifer_name', 'aquifer_material', 'aquifer_type')


admin.site.register(HydrogeologyParameter, HydrogeologyParameterAdmin)
admin.site.register(PumpingTest, PumpingTestAdmin)
