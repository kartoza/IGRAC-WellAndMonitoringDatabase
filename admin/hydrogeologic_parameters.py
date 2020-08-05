from django.contrib import admin
from gwml2.models.hydrogeology import HydrogeologyParameter, PumpingTest


class PumpingTestInline(admin.TabularInline):
    model = PumpingTest


class HydrogeologyParameterAdmin(admin.ModelAdmin):
    list_display = ('aquifer_name', 'aquifer_material', 'aquifer_type')
    inlines = [PumpingTestInline, ]


admin.site.register(HydrogeologyParameter, HydrogeologyParameterAdmin)
