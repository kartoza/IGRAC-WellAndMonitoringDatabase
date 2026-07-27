from django.contrib import admin

from gwml2.models.download_request import DownloadRequest


@admin.action(description='Run download request')
def run_download_request(modeladmin, request, queryset):
    """Trigger file generation for selected download requests."""
    from gwml2.tasks.downloader import prepare_download_file
    for obj in queryset:
        prepare_download_file(obj.id)


class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_at', 'profession', 'organization_types',
        'country', 'data_type', 'age_hours',
        'is_ready', 'is_error',
    )
    filter_horizontal = ('countries', 'organisations')
    search_fields = (
        'profession', 'country__name'
    )
    readonly_fields = ('uuid',)
    actions = (run_download_request,)
    fieldsets = (
        (None, {
            'fields': (
                'uuid', 'request_at',
                'is_ready', 'is_error', 'note',
            )
        }),
        ('Data Requested', {
            'fields': (
                'data_type', 'countries', 'organisations', 'wells_id',
            )
        }),
        ('User Information', {
            'fields': (
                'user_id', 'profession', 'organization_types', 'country',
            )
        }),
        ('Deprecated', {
            'classes': ('collapse',),
            'fields': ('email', 'first_name', 'last_name', 'organization'),
        }),
    )


admin.site.register(DownloadRequest, DownloadRequestAdmin)
