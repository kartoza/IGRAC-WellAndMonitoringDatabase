from django.contrib import admin

from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus


@admin.action(description='Create report.')
def create_report(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.create_report_excel()


@admin.action(description='Stop upload.')
def stop_upload(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.is_canceled = True
        upload_session.save()


@admin.action(description='Resume upload.')
def resume_upload(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.is_canceled = False
        upload_session.save()
        upload_session.run_in_background()


@admin.action(description='Restart upload.')
def restart_upload(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.is_canceled = False
        upload_session.save()
        upload_session.run_in_background(restart=True)


class UploadSessionAdmin(admin.ModelAdmin):
    list_display = (
        'uploaded_at',
        'is_adding',
        'is_updating',
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
    actions = (stop_upload, resume_upload, restart_upload, create_report)


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
