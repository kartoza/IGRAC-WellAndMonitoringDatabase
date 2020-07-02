from django.contrib import admin
from gwml2.models.well_construction.sealing import Sealing


class Admin(admin.ModelAdmin):
    list_display = ('sealing_grouting_placement_method',)
    filter_horizontal = ('casing_left', 'casing_slit', 'sealing_element')


admin.site.register(Sealing, Admin)
