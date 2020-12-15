from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from gwml2.models.well import (
    Well, WellDocument,
    WellQualityMeasurement, WellYieldMeasurement, WellLevelMeasurement
)

User = get_user_model()


class WellAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'organisation', 'edit', 'public')
    list_filter = ('organisation',)
    readonly_fields = ('created_at', 'created_by_user', 'last_edited_at', 'last_edited_by_user', 'ggis_uid')
    filter_horizontal = ('affiliate_organisations',)
    raw_id_fields = (
        'ground_surface_elevation', 'top_borehole_elevation', 'drilling',
        'geology', 'construction', 'management', 'hydrogeology_parameter'
    )
    list_editable = ('public',)

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


admin.site.register(WellLevelMeasurement, MeasurementAdmin)
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
