from django.contrib import admin
from gwml2.models.upload_session import (
    UploadSession, UploadSessionRowStatus
)


class UploadSessionAdmin(admin.ModelAdmin):
    list_display = (
        'uploaded_at',
        'category',
        'is_processed',
        'is_canceled'
    )
    list_filter = (
        'category',
        'is_processed',
        'is_canceled'
    )
    filter_horizontal = ('affiliate_organisations',)


admin.site.register(UploadSession, UploadSessionAdmin)


class UploadSessionRowStatusAdmin(admin.ModelAdmin):
    list_display = (
        'sheet_name',
        'row',
        'column',
        'status',
        'note'
    )
    list_filter = (
        'upload_session',
    )


admin.site.register(UploadSessionRowStatus, UploadSessionRowStatusAdmin)
