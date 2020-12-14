from django.contrib import admin
from gwml2.models.drilling import Drilling, WaterStrike, StratigraphicLog


class WaterStrikeInline(admin.TabularInline):
    model = WaterStrike
    raw_id_fields = (
        'depth',
    )


class StratigraphicLogInline(admin.TabularInline):
    model = StratigraphicLog
    raw_id_fields = (
        'top_depth', 'bottom_depth'
    )


class DrillingAdmin(admin.ModelAdmin):
    inlines = [StratigraphicLogInline, WaterStrikeInline]


admin.site.register(Drilling, DrillingAdmin)
