from django.contrib import admin

from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus


@admin.action(description='Resume upload.')
def resume_upload(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.run_in_background()


class UploadSessionAdmin(admin.ModelAdmin):
    list_display = (
        'uploaded_at',
        'category',
        'is_processed',
        'is_canceled',
        'task_id',
        'task_status'
    )
    list_filter = (
        'category',
        'is_processed',
        'is_canceled'
    )
    actions = (resume_upload,)


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
