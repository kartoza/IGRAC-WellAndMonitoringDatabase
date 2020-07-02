from django.contrib import admin
from gwml2.models.well import GWGeologyLog


class Admin(admin.ModelAdmin):
    list_display = ('phenomenon_time', 'result_time', 'gw_level', 'reference', 'start_depth', 'end_depth')


admin.site.register(GWGeologyLog, Admin)
