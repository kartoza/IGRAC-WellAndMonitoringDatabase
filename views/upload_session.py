import os

from django.core.exceptions import PermissionDenied
from django.views.generic.detail import DetailView

from gwml2.models.upload_session import UploadSession


class UploadSessionDetailView(DetailView):
    model = UploadSession
    template_name = 'upload_session/detail.html'

    def get_context_data(self, **kwargs):
        context = super(UploadSessionDetailView, self).get_context_data(
            **kwargs)
        if not self.request.user.is_superuser and self.object.uploader != self.request.user.id:
            raise PermissionDenied('You do not have permission.')

        # Create file report name
        _file = self.object.upload_file.url
        ext = os.path.splitext(_file)[1]
        _report_file = _file.replace(ext, f'.report{ext}')
        context['url'] = _report_file
        return context
