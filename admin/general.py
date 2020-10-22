from django.contrib import admin
from gwml2.models.general import Unit, UnitGroup, Country, Quantity


class UnitGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('units',)


admin.site.register(UnitGroup, UnitGroupAdmin)
admin.site.register(Unit)
admin.site.register(Quantity)
admin.site.register(Country)
