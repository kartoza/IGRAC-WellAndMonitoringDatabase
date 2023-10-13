from rest_framework import serializers

from gwml2.models.upload_session import UploadSession


class UploadSessionSerializer(serializers.ModelSerializer):
    organisation = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    report_filename = serializers.SerializerMethodField()

    def get_organisation(self, obj: UploadSession):
        return obj.organisation.name if obj.organisation else '-'

    def get_filename(self, obj: UploadSession):
        return obj.filename()

    def get_report_filename(self, obj: UploadSession):
        _report_file = obj.upload_file.url.replace('.xls', '.report.xls')
        return _report_file

    class Meta:
        model = UploadSession
        fields = [
            'id', 'organisation', 'token', 'uploaded_at', 'status', 'progress',
            'filename', 'category', 'report_filename'
        ]
