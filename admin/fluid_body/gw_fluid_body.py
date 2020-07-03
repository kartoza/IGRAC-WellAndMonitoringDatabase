from django.contrib import admin
from gwml2.models.fluid_body.gw_fluid_body import (
    BodyQualityType, VulnerabilityType, GWMetadata, GWVulnerability, GWFluidBody
)


class GWVulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('gw_vulnerability_type', 'gw_vulnerability')


class GWFluidBodyAdmin(admin.ModelAdmin):
    list_display = ('gw_body_description', 'gw_body_volume')
    filter_horizontal = ('gw_body_metadata', 'gw_body_flow', 'gw_body_quality', 'gw_body_vulnerability',
                         'gw_body_property', 'gw_body_surface', 'gw_body_constituent', 'gw_background_constituent',)


admin.site.register(VulnerabilityType)
admin.site.register(BodyQualityType)
admin.site.register(GWMetadata)
admin.site.register(GWVulnerability, GWVulnerabilityAdmin)
admin.site.register(GWFluidBody, GWFluidBodyAdmin)

