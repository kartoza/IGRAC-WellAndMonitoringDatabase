from django.contrib import admin

from gwml2.models.well_deletion import WellDeletion


class WellDeletionAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'user_val',
        'start_at'
    )


admin.site.register(WellDeletion, WellDeletionAdmin)
