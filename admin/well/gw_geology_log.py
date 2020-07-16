from django.contrib import admin
from gwml2.models.well import GWGeologyLog


class Admin(admin.ModelAdmin):
    list_display = (
        'pk', 'phenomenon_time', 'result_time', 'gw_level', 'reference', 'start_depth', 'end_depth', 'well_name')
    filter_horizontal = ('parameter',)

    def well_name(self, obj):
        try:
            wellname = obj.gw_well.gw_well_name
        except AttributeError:
            wellname = '-'
        return wellname


admin.site.register(GWGeologyLog, Admin)
