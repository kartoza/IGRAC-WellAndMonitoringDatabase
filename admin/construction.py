from django.contrib import admin
from gwml2.models.construction import Construction, ConstructionStructure


class ConstructionStructureInline(admin.TabularInline):
    model = ConstructionStructure


class ConstructionAdmin(admin.ModelAdmin):
    inlines = [ConstructionStructureInline]


admin.site.register(Construction, ConstructionAdmin)
