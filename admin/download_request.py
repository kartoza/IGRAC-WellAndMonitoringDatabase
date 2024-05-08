from django.contrib import admin

from gwml2.models.download_request import DownloadRequest


class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'first_name', 'last_name', 'organization',
        'organization_types',
        'email', 'country', 'request_at', 'age_hours'
    )
    filter_horizontal = ('countries',)
    search_fields = (
        'first_name', 'last_name', 'organization', 'email', 'country'
    )
    readonly_fields = ('uuid',)


admin.site.register(DownloadRequest, DownloadRequestAdmin)
