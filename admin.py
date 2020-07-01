from django.contrib import admin
from gwml2.models.fluid_body.gw_fluid_body import (
    GWMetadata, BodyQualityType, VulnerabilityType, GWVulnerability, GWFluidBody
)
from gwml2.models.well import GWWell, GWGeologyLog
from gwml2.models.well_construction import (
    Borehole,
    ConstructionComponent,
)
from gwml2.models.well_construction.casing_component import (
    CasingMaterialTerm, CasingCoatingTerm, CasingFormTerm, CasingComponent
)
from gwml2.models.well_construction.filtration_component import (
    FiltrationMaterialTerm, FiltrationComponent
)
from gwml2.models.well_construction.sealing_component import (
    SealingTypeTerm, SealingMaterialTerm, SealingComponent
)


class GWGeologyLogAdmin(admin.ModelAdmin):
    list_display = ('phenomenon_time', 'result_time', 'parameter', 'gw_level', 'reference', 'start_depth', 'end_depth')


# Well
admin.site.register(GWWell)
admin.site.register(GWGeologyLog, GWGeologyLogAdmin)

# Fluid Body
admin.site.register(GWMetadata)
admin.site.register(BodyQualityType)
admin.site.register(VulnerabilityType)
admin.site.register(GWVulnerability)
admin.site.register(GWFluidBody)

# Well Construction
admin.site.register(Borehole)
admin.site.register(CasingMaterialTerm)
admin.site.register(CasingCoatingTerm)
admin.site.register(CasingFormTerm)
admin.site.register(CasingComponent)
admin.site.register(ConstructionComponent)
admin.site.register(FiltrationMaterialTerm)
admin.site.register(FiltrationComponent)
admin.site.register(SealingTypeTerm)
admin.site.register(SealingMaterialTerm)
admin.site.register(SealingComponent)
