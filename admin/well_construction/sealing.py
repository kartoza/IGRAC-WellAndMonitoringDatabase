from django.contrib import admin
from gwml2.models.well_construction.sealing import Sealing


class Admin(admin.ModelAdmin):
    list_display = ('sealing_grouting_placement_method',)


admin.site.register(Sealing, Admin)
