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
        'request_at', 'first_name', 'last_name', 'organization',
        'organization_types',
        'email', 'country', 'data_type', 'age_hours',
        'is_ready', 'is_error',
    )
    filter_horizontal = ('countries', 'organisations')
    search_fields = (
        'first_name', 'last_name', 'organization', 'email', 'country'
    )
    readonly_fields = ('uuid',)
    actions = (run_download_request,)


admin.site.register(DownloadRequest, DownloadRequestAdmin)
