from django.contrib import admin

from gwml2.models.well_measurement_group_data import WellMeasurementGroupData


@admin.register(WellMeasurementGroupData)
class WellMeasurementGroupDataAdmin(admin.ModelAdmin):
    list_display = (
        'well', 'measurement_type', 'parameter', 'unit',
        'begin_measurement', 'end_measurement',
        'number_of_measurements',
    )
    list_filter = ('measurement_type',)
    search_fields = ('well__original_id',)
    readonly_fields = (
        'well', 'measurement_type', 'parameter', 'unit',
        'begin_measurement', 'end_measurement',
        'number_of_measurements',
    )
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('well', 'parameter', 'unit')

    def has_add_permission(self, request):
        return False
