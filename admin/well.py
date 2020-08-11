from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from gwml2.models.well import (
    Well, WellQualityMeasurement, WellYieldMeasurement, WellDocument,
    WellGroundwaterLevel, WellGroundwaterLevelMeasurement
)


class WellQualityMeasurementInline(admin.TabularInline):
    model = WellQualityMeasurement


class WellYieldMeasurementInline(admin.TabularInline):
    model = WellYieldMeasurement


class WellDocumentInline(admin.TabularInline):
    model = WellDocument


class WellAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'edit')
    inlines = [
        WellQualityMeasurementInline,
        WellYieldMeasurementInline,
        WellDocumentInline]

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">click here to edit well</a>',
            url)


admin.site.register(Well, WellAdmin)


class WellGroundwaterLevelMeasurementInline(admin.TabularInline):
    model = WellGroundwaterLevelMeasurement


class WellGroundwaterLevelAdmin(admin.ModelAdmin):
    inlines = [WellGroundwaterLevelMeasurementInline]


admin.site.register(WellGroundwaterLevel, WellGroundwaterLevelAdmin)
