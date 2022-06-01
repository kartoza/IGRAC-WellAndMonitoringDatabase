from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from gwml2.models.well import (
    Well, WellDocument,
    WellQualityMeasurement, WellYieldMeasurement, WellLevelMeasurement
)

User = get_user_model()


def regenerate_measurement_cache(modeladmin, request, queryset):
    for well in queryset:
        well.generate_measurement_cache()


class WellAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'organisation', 'edit', 'public', 'downloadable', 'number_of_measurements')
    list_filter = ('organisation', 'public', 'downloadable')
    readonly_fields = ('created_at', 'created_by_user', 'last_edited_at', 'last_edited_by_user', 'ggis_uid')
    raw_id_fields = (
        'ground_surface_elevation', 'top_borehole_elevation', 'drilling',
        'geology', 'construction', 'management', 'hydrogeology_parameter'
    )
    list_editable = ('public', 'downloadable')
    search_fields = ('original_id', 'name')
    actions = [regenerate_measurement_cache]

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">click here to edit well</a>',
            url)

    def created_by_user(self, obj):
        return obj.created_by_username()

    def last_edited_by_user(self, obj):
        return obj.last_edited_by_username()


admin.site.register(Well, WellAdmin)


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('well', 'time', 'parameter', 'methodology', 'value')
    search_fields = ('well__original_id',)
    raw_id_fields = (
        'value',
    )


class WellLevelMeasurementAdmin(MeasurementAdmin):
    list_display = ('well', 'time', 'parameter', 'methodology', 'value', 'value_in_m')
    readonly_fields = ('value_in_m',)


admin.site.register(WellLevelMeasurement, WellLevelMeasurementAdmin)
admin.site.register(WellQualityMeasurement, MeasurementAdmin)
admin.site.register(WellYieldMeasurement, MeasurementAdmin)


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
