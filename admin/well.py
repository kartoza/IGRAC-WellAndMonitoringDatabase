from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from gwml2.models.well import Well, WellMeasurement, WellDocument


class WellMeasurementInline(admin.TabularInline):
    model = WellMeasurement


class WellDocumentInline(admin.TabularInline):
    model = WellDocument


class WellAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'edit')
    inlines = [WellMeasurementInline, WellDocumentInline]

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">click here to edit well</a>',
            url)


admin.site.register(Well, WellAdmin)
