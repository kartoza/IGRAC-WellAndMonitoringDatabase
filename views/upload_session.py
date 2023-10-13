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
        context['url'] = self.object.upload_file.url.replace(
            '.xls', '.report.xls'
        )
        return context
