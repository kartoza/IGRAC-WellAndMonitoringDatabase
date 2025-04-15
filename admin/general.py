from django.contrib import admin

from gwml2.models.general import (
    Unit, UnitConvertion, UnitGroup, Country, Quantity
)
from gwml2.utils.management_commands import run_command


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


@admin.action(description='Generate data cache')
def generate_data_wells_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'generate_data_countries_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'data_cache_generated_at')
    list_filter = ('data_cache_generated_at',)
    actions = (generate_data_wells_cache,)
    search_fields = ('name',)
