from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from gwml2.models.well_cache_indicator import WellCacheIndicator
from gwml2.models.well_management.organisation import Organisation, Country
from gwml2.utils.management_commands import run_command


class OrganisationFilter(admin.SimpleListFilter):
    title = 'Organisation'
    parameter_name = 'organisation'

    def lookups(self, request, model_admin):
        """Return a list of tuples (value, label) for the filter dropdown."""
        return [
            (a.id, a.name) for a in Organisation.objects.all()
        ]

    def queryset(self, request, queryset):
        """Filter queryset based on the selected value."""
        if self.value():
            return queryset.filter(well__organisation_id=self.value())
        return queryset


class CountryFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        """Return a list of tuples (value, label) for the filter dropdown."""
        return [
            (a.id, a.name) for a in Country.objects.all()
        ]

    def queryset(self, request, queryset):
        """Filter queryset based on the selected value."""
        if self.value():
            return queryset.filter(well__country_id=self.value())
        return queryset


@admin.action(description='Generate data cache')
def generate_data_wells_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('well_id', flat=True)]
    return run_command(
        request,
        'generate_data_wells_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.action(description='Generate measurement cache')
def generate_measurement_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('well_id', flat=True)]
    return run_command(
        request,
        'generate_well_measurement_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.action(description='Generate metadata')
def generate_metadata(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('well_id', flat=True)]
    return run_command(
        request,
        'generate_well_metadata',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.register(WellCacheIndicator)
class WellCacheIndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'well', '_organisation', '_country',
        'measurement_cache_generated_at',
        'data_cache_generated_at',
        'metadata_generated_at',
        'edit'
    )
    change_list_template = "admin/well_cache_change_list.html"
    actions = [
        generate_data_wells_cache, generate_measurement_cache,
        generate_metadata
    ]

    list_filter = (
        OrganisationFilter, CountryFilter
    )
    readonly_fields = ('well',)
    search_fields = ('well__original_id',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'well', 'well__organisation', 'well__country'
        ).only(
            'well__original_id',
            'well__organisation__id', 'well__organisation__name',
            'well__country__id', 'well__country__name'
        )

    @admin.display(ordering='well__organisation__name')
    def _organisation(self, obj: WellCacheIndicator):
        return obj.well.organisation

    @admin.display(ordering='well__country__name')
    def _country(self, obj: WellCacheIndicator):
        return obj.well.country

    def edit(self, obj: WellCacheIndicator):
        url = reverse('well_form', args=[obj.well.id])
        return format_html(
            '<a href="{}" target="_blank">Edit well</a>',
            url
        )
