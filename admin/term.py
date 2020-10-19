from django.contrib import admin
from adminsortable.admin import SortableAdmin
from gwml2.models.term import (
    TermAquiferType, TermConfinement, TermDrillingMethod, TermWellPurpose, TermWellStatus,
    TermFeatureType, TermGroundwaterUse, TermMeasurementParameter,
    TermReferenceElevationType, TermConstructionStructureType, TermMeasurementParameterGroup
)


class TermMeasurementParameterGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('parameters',)


admin.site.register(TermAquiferType, SortableAdmin)
admin.site.register(TermConfinement, SortableAdmin)
admin.site.register(TermConstructionStructureType, SortableAdmin)
admin.site.register(TermDrillingMethod, SortableAdmin)
admin.site.register(TermFeatureType, SortableAdmin)
admin.site.register(TermGroundwaterUse, SortableAdmin)
admin.site.register(TermMeasurementParameter, SortableAdmin)
admin.site.register(TermReferenceElevationType, SortableAdmin)
admin.site.register(TermWellPurpose, SortableAdmin)
admin.site.register(TermWellStatus, SortableAdmin)
admin.site.register(TermMeasurementParameterGroup, TermMeasurementParameterGroupAdmin)
