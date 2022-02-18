from django.contrib import admin
from gwml2.models.download_session import (
    DownloadSession, DownloadSessionUser
)


class DownloadSessionUserline(admin.TabularInline):
    model = DownloadSessionUser


class DownloadSessionAdmin(admin.ModelAdmin):
    inlines = [DownloadSessionUserline]
    list_display = (
        'token',
        'start_at',
        'filters',
        'progress',
        'obsolete',
        'well'
    )
    list_editable = ('obsolete',)


admin.site.register(DownloadSession, DownloadSessionAdmin)
