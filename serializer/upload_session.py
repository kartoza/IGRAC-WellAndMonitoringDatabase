from rest_framework import serializers

from gwml2.models.upload_session import (
    UploadSession, UploadSessionRowStatus
)


class UploadSessionSerializer(serializers.ModelSerializer):
    organisation = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    report_filenames = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()

    def get_file_url(self, obj: UploadSession):
        return obj.upload_file.url

    def get_organisation(self, obj: UploadSession):
        return obj.organisation.name if obj.organisation else '-'

    def get_report_filenames(self, obj: UploadSession):
        return obj.file_report_urls

    def get_uploaded_at(self, obj: UploadSession):
        return obj.timestamp

    class Meta:
        model = UploadSession
        fields = [
            'id', 'organisation', 'token', 'uploaded_at', 'status', 'progress',
            'filename', 'category', 'report_filenames', 'is_processed',
            'is_canceled', 'task_status', 'step', 'file_url', 'retry'
        ]


class UploadSessionRowStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = UploadSessionRowStatus
        fields = [
            'sheet_name', 'row', 'column', 'status', 'status_display', 'note'
        ]
