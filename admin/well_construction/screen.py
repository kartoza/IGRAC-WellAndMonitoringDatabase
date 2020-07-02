from django.contrib import admin
from gwml2.models.well_construction.screen import Screen


class Admin(admin.ModelAdmin):
    filter_horizontal = ('screen_element',)


admin.site.register(Screen, Admin)
