from django.contrib import admin
from gwml2.models.drilling_and_construction import (
    DrillingAndConstruction, Casing, Screening, WaterStrike
)


class CasingInline(admin.TabularInline):
    model = Casing


class ScreeningInline(admin.TabularInline):
    model = Screening


class WaterStrikeInline(admin.TabularInline):
    model = WaterStrike


class DrillingAndConstructionAdmin(admin.ModelAdmin):
    inlines = [CasingInline, ScreeningInline, WaterStrikeInline]


admin.site.register(DrillingAndConstruction, DrillingAndConstructionAdmin)
