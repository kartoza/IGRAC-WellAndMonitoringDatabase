from django.contrib import admin
from gwml2.models.geology import Geology


class GeologyAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'total_depth',
    )


admin.site.register(Geology, GeologyAdmin)
