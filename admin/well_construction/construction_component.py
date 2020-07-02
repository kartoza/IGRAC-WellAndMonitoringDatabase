from django.contrib import admin
from gwml2.models.well_construction.construction_component import (
    ConstructionComponent
)


class Admin(admin.ModelAdmin):
    list_display = ('from_component', 'to_component')


admin.site.register(ConstructionComponent, Admin)
