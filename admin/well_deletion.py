from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe  # Newer versions

from gwml2.models.well_deletion import WellDeletion
from gwml2.tasks.well import run_well_deletion


def run(modeladmin, request, queryset):
    for obj in queryset:
        run_well_deletion.delay(obj.id)


class WellDeletionAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'user_val',
        'start_at',
        '_progress',
        'detail'
    )

    def detail(self, obj):
        return mark_safe(
            f'<a href="{reverse("delete-well-progress-view", args=[obj.identifier])}">detail</a>'
        )

    def _progress(self, obj):
        return f'{obj.progress}%'

    _progress.short_description = "progress"
    actions = [run]


admin.site.register(WellDeletion, WellDeletionAdmin)
