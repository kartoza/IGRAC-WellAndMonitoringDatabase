from adminsortable.admin import SortableAdmin
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


class TermMeasurementParameterAdmin(SortableAdmin):
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
admin.site.register(
    TermMeasurementParameterGroup,
    TermMeasurementParameterGroupAdmin
)
