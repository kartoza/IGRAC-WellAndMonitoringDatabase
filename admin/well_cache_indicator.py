import json

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from gwml2.admin.well import InputFilter
from gwml2.models.well_cache_indicator import WellCacheIndicator
from gwml2.models.well_management.organisation import Organisation, Country
from gwml2.utils.management_commands import run_command


class MeasurementCacheFromFilter(InputFilter):
    title = 'Measurement cache from'
    parameter_name = 'measurement_cache_from'
    input_type = 'date'
    lookup = 'measurement_cache_generated_at__date__gte'


class MeasurementCacheToFilter(InputFilter):
    title = 'Measurement cache to'
    parameter_name = 'measurement_cache_to'
    input_type = 'date'
    lookup = 'measurement_cache_generated_at__date__lte'


class DataCacheFromFilter(InputFilter):
    title = 'Data cache from'
    parameter_name = 'data_cache_from'
    input_type = 'date'
    lookup = 'data_cache_generated_at__date__gte'


class DataCacheToFilter(InputFilter):
    title = 'Data cache to'
    parameter_name = 'data_cache_to'
    input_type = 'date'
    lookup = 'data_cache_generated_at__date__lte'


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


@admin.action(description='Generate data cache information')
def generate_data_cache_information(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('well_id', flat=True)]
    return run_command(
        request,
        'generate_data_cache_information',
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
        'data_cache_info',
        'links'
    )
    change_list_template = "admin/well_cache_change_list.html"
    actions = [
        generate_data_wells_cache, generate_measurement_cache,
        generate_metadata, generate_data_cache_information
    ]
    list_filter = (
        'well__feature_type',
        OrganisationFilter, CountryFilter,
        MeasurementCacheFromFilter, MeasurementCacheToFilter,
        DataCacheFromFilter, DataCacheToFilter,
    )
    readonly_fields = ('well',)
    search_fields = ('well__original_id',)
    show_full_result_count = False

    def get_urls(self):
        opts = self.model._meta
        custom = [
            path(
                'count/',
                self.admin_site.admin_view(self.count_view),
                name=f'{opts.app_label}_{opts.model_name}_count',
            ),
        ]
        return custom + super().get_urls()

    def count_view(self, request):
        return JsonResponse({'count': self.get_queryset(request).count()})

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'well', 'well__organisation', 'well__country'
        ).only(
            'well__id',
            'well__original_id',
            'well__organisation__id', 'well__organisation__name',
            'well__country__id', 'well__country__name',
            'measurement_cache_generated_at',
            'data_cache_generated_at',
            'metadata_generated_at',
            'data_cache_information',
        )

    @admin.display(ordering='well__organisation__name')
    def _organisation(self, obj: WellCacheIndicator):
        return obj.well.organisation

    @admin.display(ordering='well__country__name')
    def _country(self, obj: WellCacheIndicator):
        return obj.well.country

    def links(self, obj: WellCacheIndicator):
        well_id = obj.well.id
        url = reverse('well_form', args=[well_id])
        return format_html(
            '<a href="{}" target="_blank">Edit well</a><br/>'
            '<a href="/admin/gwml2/welllevelmeasurement/?well_id__exact={}" target="_blank">Level Measurements</a><br/>'
            '<a href="/admin/gwml2/wellqualitymeasurement/?well_id__exact={}" target="_blank">Quality Measurements</a><br/>'
            '<a href="/admin/gwml2/wellyieldmeasurement/?well_id__exact={}" target="_blank">Yield Measurements</a>',
            url, well_id, well_id, well_id
        )

    def data_cache_info(self, obj):
        if not obj.data_cache_information:
            return "-"
        try:
            single_line = json.dumps(obj.data_cache_information)
            return format_html(
                f"<div style='white-space: nowrap'>"
                f"{single_line.replace('{', '').replace('}', '')}"
                f"</div>"
            )
        except Exception as e:
            print(e)
            return str(obj.data_cache_information)

    data_cache_info.short_description = "Data cache information"
