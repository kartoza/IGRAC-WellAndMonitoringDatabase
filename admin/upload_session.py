from django.contrib import admin

from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus


class RunningUploaderFilter(admin.SimpleListFilter):
    """Return running uploader."""

    title = 'Running uploader'
    parameter_name = 'is_runnin_uploader'

    def lookups(self, request, model_admin):
        """Lookup function for entity filter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        if self.value() == "yes":
            return queryset.filter(
                is_processed=False,
                is_canceled=False,
                progress__lt=100
            )
        if self.value() == "no":
            return queryset.exclude(
                is_processed=False,
                is_canceled=False,
                progress__lt=100
            )
        return queryset


@admin.action(description='Create report.')
def create_report(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.create_report_excel()


@admin.action(description='Stop upload.')
def stop_upload(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.stop()


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
        'is_canceled',
        RunningUploaderFilter
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
