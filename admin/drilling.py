from django.contrib import admin
from gwml2.models.drilling import Drilling, WaterStrike, StratigraphicLog


class WaterStrikeInline(admin.TabularInline):
    model = WaterStrike


class StratigraphicLogInline(admin.TabularInline):
    model = StratigraphicLog


class DrillingAdmin(admin.ModelAdmin):
    inlines = [StratigraphicLogInline, WaterStrikeInline]


admin.site.register(Drilling, DrillingAdmin)
