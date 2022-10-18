from django.contrib import admin

from gwml2.models.download_request import DownloadRequest


class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'surname', 'organisation', 'position', 'email', 'request_at')
    filter_horizontal = ('countries',)
    search_fields = ('name', 'surname', 'organisation', 'email')


admin.site.register(DownloadRequest, DownloadRequestAdmin)
