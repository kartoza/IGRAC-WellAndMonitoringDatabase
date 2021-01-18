from django.contrib import admin
from gwml2.models.construction import Construction, ConstructionStructure


class ConstructionStructureInline(admin.TabularInline):
    model = ConstructionStructure
    raw_id_fields = (
        'top_depth', 'bottom_depth', 'diameter'
    )


class ConstructionAdmin(admin.ModelAdmin):
    inlines = [ConstructionStructureInline]


admin.site.register(Construction, ConstructionAdmin)
