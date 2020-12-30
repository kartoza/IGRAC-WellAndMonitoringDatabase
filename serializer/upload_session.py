from rest_framework import serializers
from gwml2.models.upload_session import UploadSession


class UploadSessionSerializer(serializers.ModelSerializer):
    organisation = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    def get_organisation(self, obj: UploadSession):
        return obj.organisation.name if obj.organisation else '-'

    def get_filename(self, obj: UploadSession):
        return obj.filename()

    class Meta:
        model = UploadSession
        fields = ['organisation', 'token', 'uploaded_at', 'status', 'progress', 'filename', 'category']
