from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.db import connections
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html

from gwml2.models.site_preference import SitePreference
from gwml2.models.well import (
    Well, WellDocument, Measurement,
    WellQualityMeasurement, WellYieldMeasurement, WellLevelMeasurement
)
from gwml2.models.well_materialized_view import MaterializedViewWell
from gwml2.utils.management_commands import run_command

User = get_user_model()

bbox = Polygon(
    (
        (-180, -90),
        (-180, 90),
        (180, 90),
        (180, -90),
        (-180, -90)
    )
)


class InvalidCoordinatesFilter(admin.SimpleListFilter):
    """Invalid coordinates filter."""

    title = 'Invalid coordinates'
    parameter_name = 'is_invalid_coordinates'

    def lookups(self, request, model_admin):
        """Lookup function for entity filter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        if self.value() == "yes":
            return queryset.filter(
                Q(location__isnull=True) |
                ~Q(location__within=bbox)
            )
        if self.value() == "no":
            return queryset.filter(
                location__isnull=False,
                location__within=bbox
            )
        return queryset


def assign_country(modeladmin, request, queryset):
    for well in queryset:
        well.assign_country(force=True)


@admin.action(description='Delete selected wells in background')
def delete_in_background(modeladmin, request, queryset):
    from gwml2.views.admin.delete_selected_confirmation_background import (
        delete_well_in_background
    )
    return delete_well_in_background(modeladmin, request, queryset)


@admin.action(description='Generate data cache')
def generate_data_wells_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
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
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'generate_well_measurement_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.action(description='Generate measurement cache generated at field')
def generate_measurement_cache_generated_at(modeladmin, request, queryset):
    """Generate measurement cache at field."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'update_measurement_cache_generated_at',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.action(description='Change from ground to a.m.s.l')
def change_ground_to_amsl(modeladmin, request, queryset):
    """Change measurement from ground to a.m.s.l."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    preference = SitePreference.load()
    if preference.parameter_from_ground_surface and preference.parameter_amsl:
        if (
                preference.parameter_from_ground_surface !=
                preference.parameter_amsl
        ):
            return run_command(
                request,
                'convert_measurement_parameter',
                args=[
                    "--ids", ', '.join(ids),
                    "--from_measurement_id",
                    preference.parameter_from_ground_surface.id,
                    "--to_measurement_id",
                    preference.parameter_amsl.id,
                ]
            )


class WellAdmin(admin.ModelAdmin):
    list_display = (
        'original_id', 'organisation', 'number_of_measurements',
        'latitude', 'longitude',
        'country', 'id',
        'first_time_measurement', 'last_time_measurement',
        'edit', '_measurement_cache_generated',
        '_data_cache_generated'
    )
    list_filter = (
        'organisation', 'country', 'feature_type',
        'first_time_measurement', 'last_time_measurement',
        'measurement_cache_generated_at',
        'data_cache_generated_at',
        InvalidCoordinatesFilter
    )
    readonly_fields = (
        'created_at', 'created_by_user', 'last_edited_at',
        'last_edited_by_user',
        'ggis_uid'
    )
    raw_id_fields = (
        'ground_surface_elevation', 'top_borehole_elevation',
        'glo_90m_elevation', 'drilling',
        'geology', 'construction', 'management', 'hydrogeology_parameter'
    )
    search_fields = ('original_id', 'name')
    actions = [
        delete_in_background,
        generate_data_wells_cache,
        generate_measurement_cache,
        assign_country
    ]

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">Edit well</a>',
            url)

    def created_by_user(self, obj):
        return obj.created_by_username()

    def last_edited_by_user(self, obj):
        return obj.last_edited_by_username()

    def latitude(self, obj: Well):
        return obj.location.y

    def longitude(self, obj: Well):
        return obj.location.x

    def _measurement_cache_generated(self, obj: Well):
        return obj.measurement_cache_generated_at

    def _data_cache_generated(self, obj: Well):
        return obj.data_cache_generated_at

    _measurement_cache_generated.admin_order_field = 'measurement_cache_generated_at'
    _data_cache_generated.admin_order_field = 'data_cache_generated_at'


admin.site.register(Well, WellAdmin)


def refresh(modeladmin, request, queryset):
    """Refresh materialized view."""
    with connections['gwml2'].cursor() as cursor:
        cursor.execute('REFRESH MATERIALIZED VIEW mv_well;')


@admin.register(MaterializedViewWell)
class MaterializedViewWellAdmin(admin.ModelAdmin):
    list_display = (
        'ggis_uid', 'id', 'name', 'organisation',
        'country', 'first_time_measurement', 'last_time_measurement',
        'number_of_measurements_level', 'number_of_measurements_quality',
        'is_groundwater_level', 'is_groundwater_quality',
        'link',
    )
    list_filter = (
        'first_time_measurement', 'last_time_measurement'
    )
    search_fields = ('ggis_uid', 'name')
    actions = (refresh,)

    def link(self, obj):
        return format_html(obj.detail)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('well', 'uploaded_at', 'file')
    search_fields = ('well__original_id',)

    def file(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">click here to edit well</a>',
                obj.file.url)
        else:
            return '-'


admin.site.register(WellDocument, DocumentAdmin)


# --------------------------------------------------------------------
# MEASUREMENTS
# --------------------------------------------------------------------


class PageSizeFilter(SimpleListFilter):
    title = 'Page size'
    parameter_name = 'page_size'

    def lookups(self, request, model_admin):
        """Lookups."""
        return [
            ('10', '10'),
            ('100', '100'),
            ('250', '250'),
            ('500', '500'),
            ('1000', '1000'),
            ('5000', '5000'),
            ('10000', '10000'),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        return queryset


class PageSizeChangeList(ChangeList):
    """Page size change list."""

    def get_results(self, request):
        self.list_per_page = self.get_page_size(request)
        super().get_results(request)

    def get_page_size(self, request):
        try:
            return int(request.GET.get('page_size', self.list_per_page))
        except (TypeError, ValueError):
            return self.list_per_page


class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        '_well_id', 'time', 'parameter_name', '_default_unit', 'default_value'
    )
    search_fields = ('well__original_id',)
    raw_id_fields = ('value',)
    list_filter = (PageSizeFilter, 'time')
    change_list_template = "admin/measurements_change_list.html"

    def get_changelist(self, request, **kwargs):
        return PageSizeChangeList

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['page_size'] = request.GET.get(
            'page_size', self.list_per_page
        )
        return super().changelist_view(request, extra_context=extra_context)

    def _well_id(self, obj: WellLevelMeasurement):
        return obj.well_id

    def parameter_name(self, obj: Measurement):
        return obj.parameter.__str__()

    def _default_unit(self, obj: Measurement):
        return obj.default_unit.__str__()

    _well_id.short_description = 'Well ID'
    _well_id.admin_order_field = 'well_id'
    parameter_name.admin_order_field = 'parameter'


admin.site.register(WellLevelMeasurement, MeasurementAdmin)
admin.site.register(WellQualityMeasurement, MeasurementAdmin)
admin.site.register(WellYieldMeasurement, MeasurementAdmin)
