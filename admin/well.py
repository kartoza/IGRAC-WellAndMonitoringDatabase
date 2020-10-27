from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from gwml2.models.well import (
    Well, WellDocument,
    WellQualityMeasurement, WellYieldMeasurement, WellLevelMeasurement
)


class WellAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'edit')

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">click here to edit well</a>',
            url)


admin.site.register(Well, WellAdmin)


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('well', 'time', 'parameter', 'methodology', 'value')
    search_fields = ('well__original_id',)


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
