from django.contrib import admin
from gwml2.models.well import GWGeologyLog


class Admin(admin.ModelAdmin):
    list_display = (
        'pk', 'phenomenon_time', 'result_time', 'gw_level', 'reference', 'start_depth', 'end_depth', 'well_name')
    filter_horizontal = ('parameter',)

    def well_name(self, obj):
        return obj.gw_well.gw_well_name


admin.site.register(GWGeologyLog, Admin)
