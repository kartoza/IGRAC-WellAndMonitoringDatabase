from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html

from gwml2.models.well import (
    Well, WellDocument,
    WellQualityMeasurement, WellYieldMeasurement, WellLevelMeasurement
)

User = get_user_model()


def assign_country(modeladmin, request, queryset):
    for well in queryset:
        well.assign_country(force=True)


def regenerate_measurement_cache(modeladmin, request, queryset):
    for well in queryset:
        well.generate_measurement_cache()


@admin.action(description='Delete selected wells in background')
def delete_in_background(modeladmin, request, queryset):
    from gwml2.views.admin.delete_selected_confirmation_background import (
        delete_well_in_background
    )
    return delete_well_in_background(modeladmin, request, queryset)


class WellAdmin(admin.ModelAdmin):
    list_display = (
        'original_id', 'organisation', 'number_of_measurements',
        'country', 'id', 'last_measurements',
        'first_time_measurement', 'last_time_measurement',
        'edit',
    )
    list_filter = (
        'organisation', 'country',
        'first_time_measurement', 'last_time_measurement'
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
        delete_in_background, regenerate_measurement_cache, assign_country
    ]

    def edit(self, obj):
        url = reverse('well_form', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">Edit well</a>',
            url)

    def last_measurements(self, obj: Well):
        last_data = {}
        query = obj.welllevelmeasurement_set.all()
        if query.count():
            last_data['level'] = query[0].time.strftime("%Y-%m-%d, %H:%M:%S")
        query = obj.wellyieldmeasurement_set.all()
        if query.count():
            last_data['yield'] = query[0].time.strftime("%Y-%m-%d, %H:%M:%S")
        query = obj.wellqualitymeasurement_set.all()
        if query.count():
            last_data['quality'] = query[0].time.strftime("%Y-%m-%d, %H:%M:%S")
        return last_data

    def created_by_user(self, obj):
        return obj.created_by_username()

    def last_edited_by_user(self, obj):
        return obj.last_edited_by_username()


admin.site.register(Well, WellAdmin)


class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        'well', 'time', 'parameter', 'methodology', 'value',
        'default_unit', 'default_value'
    )
    search_fields = ('well__original_id',)
    raw_id_fields = (
        'value',
    )


class WellLevelMeasurementAdmin(MeasurementAdmin):
    list_display = (
        'well', 'time', 'parameter', 'methodology', 'value', 'value_in_m',
        'default_unit', 'default_value'
    )
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
