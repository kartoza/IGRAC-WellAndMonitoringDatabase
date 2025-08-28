from django.contrib import admin

from gwml2.models.term import (
    TermAquiferType, TermConfinement, TermDrillingMethod, TermWellPurpose,
    TermWellStatus,
    TermFeatureType, TermGroundwaterUse,
    TermReferenceElevationType, TermConstructionStructureType
)
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameter,
    TermMeasurementParameterGroup
)


class TermMeasurementParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_list', 'default_unit', 'groups')
    filter_horizontal = ('units',)
    list_editable = ('default_unit',)

    def unit_list(self, obj: TermMeasurementParameter):
        return ', '.join(obj.units.values_list('name', flat=True))

    def groups(self, obj: TermMeasurementParameter):
        return ', '.join(
            obj.termmeasurementparametergroup_set.values_list(
                'name', flat=True
            )
        )


class TermMeasurementParameterGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('parameters',)


admin.site.register(TermAquiferType, admin.ModelAdmin)
admin.site.register(TermConfinement, admin.ModelAdmin)
admin.site.register(TermConstructionStructureType, admin.ModelAdmin)
admin.site.register(TermDrillingMethod, admin.ModelAdmin)
admin.site.register(TermFeatureType, admin.ModelAdmin)
admin.site.register(TermGroundwaterUse, admin.ModelAdmin)
admin.site.register(TermMeasurementParameter, TermMeasurementParameterAdmin)
admin.site.register(TermReferenceElevationType, admin.ModelAdmin)
admin.site.register(TermWellPurpose, admin.ModelAdmin)
admin.site.register(TermWellStatus, admin.ModelAdmin)
admin.site.register(
    TermMeasurementParameterGroup,
    TermMeasurementParameterGroupAdmin
)
