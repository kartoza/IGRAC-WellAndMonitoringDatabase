from django.contrib import admin
from gwml2.models.well_construction.casing import Casing


class Admin(admin.ModelAdmin):
    filter_horizontal = ('casing_element',)


admin.site.register(Casing, Admin)
