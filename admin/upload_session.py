from datetime import timedelta

from django.contrib import admin, messages
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus
from gwml2.tasks.uploader.task import well_batch_upload_create_report

FILE_DELETION_MIN_AGE = timedelta(weeks=1)


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
        well_batch_upload_create_report.delay(upload_session.id)


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


@admin.action(description='Clean row status.')
def clean_row_status(modeladmin, request, queryset):
    for upload_session in queryset:
        upload_session.clean_row_status()


def delete_old_files(modeladmin, request, queryset, get_names):
    """Delete files returned by get_names for sessions older than 1 week."""
    cutoff = timezone.now() - FILE_DELETION_MIN_AGE
    skipped = 0
    for upload_session in queryset:
        if upload_session.uploaded_at > cutoff:
            skipped += 1
            continue
        storage = upload_session.upload_file.storage
        for name in get_names(upload_session):
            if name and storage.exists(name):
                storage.delete(name)
    if skipped:
        modeladmin.message_user(
            request,
            f'{skipped} upload session(s) skipped because they are not '
            f'older than {FILE_DELETION_MIN_AGE.days} days yet.',
            level=messages.WARNING
        )


@admin.action(description='Delete uploaded file (space saving).')
def delete_uploaded_file(modeladmin, request, queryset):
    delete_old_files(
        modeladmin, request, queryset,
        lambda upload_session: [upload_session.upload_file.name]
    )


@admin.action(description='Delete report file (space saving).')
def delete_report_file(modeladmin, request, queryset):
    delete_old_files(
        modeladmin, request, queryset,
        lambda upload_session: upload_session.report_file_candidates()
    )


def file_link_with_size(storage, name, url):
    """Return html link to file, with its size appended if it exists."""
    size_label = ''
    try:
        if storage.exists(name):
            size_label = f' ({filesizeformat(storage.size(name))})'
    except Exception:
        pass
    return format_html(
        '<a href="{url}" target="_blank">{url}</a>{size}',
        url=url,
        size=size_label
    )


class UploadSessionAdmin(admin.ModelAdmin):
    list_display = (
        'uploaded_at',
        'is_adding',
        'is_updating',
        'category',
        'is_processed',
        'is_canceled',
        'task_id',
        'task_status',
        'file_uploaded',
        'file_report',
        'retry'
    )
    list_filter = (
        'category',
        'is_processed',
        'is_canceled',
        RunningUploaderFilter
    )
    actions = (
        stop_upload, resume_upload, restart_upload, create_report,
        clean_row_status, delete_uploaded_file, delete_report_file
    )

    def file_uploaded(self, obj: UploadSession):
        """File uploaded."""
        return file_link_with_size(
            obj.upload_file.storage, obj.upload_file.name, obj.upload_file.url
        )

    def file_report(self, obj: UploadSession):
        """File report."""
        storage = obj.upload_file.storage
        report_names = obj.existing_report_files
        if not report_names:
            return '-'
        return mark_safe('<br>'.join(
            file_link_with_size(storage, name, storage.url(name))
            for name in report_names
        ))


admin.site.register(UploadSession, UploadSessionAdmin)


class UploadSessionRowStatusAdmin(admin.ModelAdmin):
    list_display = (
        'sheet_name',
        'row',
        'column',
        'status',
        'note',
        'well'
    )
    list_filter = (
        'upload_session', 'status'
    )
    raw_id_fields = ('well',)


admin.site.register(UploadSessionRowStatus, UploadSessionRowStatusAdmin)
