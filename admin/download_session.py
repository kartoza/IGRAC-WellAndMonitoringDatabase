from django.contrib import admin
from gwml2.models.download_session import (
    DownloadSession
)


class DownloadSessionAdmin(admin.ModelAdmin):
    list_display = (
        'token',
        'uploaded_at',
        'filters',
        'progress'
    )


admin.site.register(DownloadSession, DownloadSessionAdmin)
