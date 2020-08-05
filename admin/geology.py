from django.contrib import admin
from gwml2.models.geology import Geology, GeologyLog


class GeologyLogInline(admin.TabularInline):
    model = GeologyLog


class GeologyAdmin(admin.ModelAdmin):
    inlines = [GeologyLogInline, ]


admin.site.register(Geology, GeologyAdmin)
