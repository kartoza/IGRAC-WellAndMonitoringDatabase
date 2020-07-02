from django.contrib import admin
from gwml2.models.well_construction.filtration import Filtration


class Admin(admin.ModelAdmin):
    filter_horizontal = ('filter_element',)


admin.site.register(Filtration, Admin)
