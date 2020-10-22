from django.contrib import admin
from adminsortable.admin import SortableAdmin
from gwml2.models.term import (
    TermAquiferType, TermConfinement, TermDrillingMethod, TermWellPurpose, TermWellStatus,
    TermFeatureType, TermGroundwaterUse,
    TermReferenceElevationType, TermConstructionStructureType
)
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter,
    TermMeasurementParameterGroup
)


class TermMeasurementParameterAdmin(SortableAdmin):
    filter_horizontal = ('units',)


class TermMeasurementParameterGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('parameters',)


admin.site.register(TermAquiferType, SortableAdmin)
admin.site.register(TermConfinement, SortableAdmin)
admin.site.register(TermConstructionStructureType, SortableAdmin)
admin.site.register(TermDrillingMethod, SortableAdmin)
admin.site.register(TermFeatureType, SortableAdmin)
admin.site.register(TermGroundwaterUse, SortableAdmin)
admin.site.register(TermMeasurementParameter, TermMeasurementParameterAdmin)
admin.site.register(TermReferenceElevationType, SortableAdmin)
admin.site.register(TermWellPurpose, SortableAdmin)
admin.site.register(TermWellStatus, SortableAdmin)
admin.site.register(TermMeasurementParameterGroup, TermMeasurementParameterGroupAdmin)
