from django.contrib import admin

from gwml2.models.general import (
    Unit, UnitConvertion, UnitGroup, Country, Quantity
)


class UnitConvertionInline(admin.TabularInline):
    fk_name = "unit_from"
    model = UnitConvertion


class UnitGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('units',)


class UnitAdmin(admin.ModelAdmin):
    inlines = [UnitConvertionInline]


admin.site.register(UnitGroup, UnitGroupAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Quantity)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
