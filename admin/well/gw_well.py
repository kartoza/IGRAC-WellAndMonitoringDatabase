from django.contrib import admin
from gwml2.models.well.gw_well import WellStatusTypeTerm, GWLicence, GWWell


class GWLicenceAdmin(admin.ModelAdmin):
    list_display = ('gw_licence_id', 'gw_purpose', 'gw_associated_gw_volume', 'gw_time_period')


class GWWellAdmin(admin.ModelAdmin):
    list_display = ('gw_well_name',)


admin.site.register(WellStatusTypeTerm)
admin.site.register(GWLicence, GWLicenceAdmin)
admin.site.register(GWWell, GWWellAdmin)
