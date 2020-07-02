from django.contrib import admin
from gwml2.models.well_construction.equipment import (
    Equipment, EquipmentCharacteristicTerm, EquipmentTypeTerm
)


class Admin(admin.ModelAdmin):
    filter_horizontal = ('characteristics',)


admin.site.register(EquipmentCharacteristicTerm)
admin.site.register(EquipmentTypeTerm)
admin.site.register(Equipment, Admin)
