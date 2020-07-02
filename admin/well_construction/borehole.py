from django.contrib import admin
from gwml2.models.well_construction.borehole import Borehole


class Admin(admin.ModelAdmin):
    filter_horizontal = ('installed_equipment', 'bhole_material_custodian', 'bhole_drilling_method')


admin.site.register(Borehole, Admin)
