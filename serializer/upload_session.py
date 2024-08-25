import os

from rest_framework import serializers

from gwml2.models.upload_session import UploadSession


class UploadSessionSerializer(serializers.ModelSerializer):
    organisation = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    report_filename = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()

    def get_file_url(self, obj: UploadSession):
        return obj.upload_file.url

    def get_organisation(self, obj: UploadSession):
        return obj.organisation.name if obj.organisation else '-'

    def get_report_filename(self, obj: UploadSession):
        _file = obj.upload_file.url
        _path = obj.upload_file.path
        ext = os.path.splitext(_file)[1]
        _report_file = _file.replace(ext, f'.report{ext}')
        _report_path = _path.replace(ext, f'.report{ext}')
        if os.path.exists(_report_path):
            return _report_file
        else:
            return None

    def get_uploaded_at(self, obj: UploadSession):
        return obj.timestamp

    class Meta:
        model = UploadSession
        fields = [
            'id', 'organisation', 'token', 'uploaded_at', 'status', 'progress',
            'filename', 'category', 'report_filename', 'is_processed',
            'is_canceled', 'task_status', 'step', 'file_url'
        ]
