from django.contrib import admin
from gwml2.models.drilling_and_construction import (
    DrillingAndConstruction, Casing, Screen, WaterStrike
)


class CasingInline(admin.TabularInline):
    model = Casing


class ScreenInline(admin.TabularInline):
    model = Screen


class WaterStrikeInline(admin.TabularInline):
    model = WaterStrike


class DrillingAndConstructionAdmin(admin.ModelAdmin):
    inlines = [CasingInline, ScreenInline, WaterStrikeInline]


admin.site.register(DrillingAndConstruction, DrillingAndConstructionAdmin)
