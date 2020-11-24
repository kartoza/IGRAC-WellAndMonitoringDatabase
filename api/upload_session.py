from django.http import JsonResponse, Http404
from django.views.generic.base import View
from gwml2.models.upload_session import UploadSession


class UploadSessionApiView(View):
    """
    Return status of the upload session
    """

    def get(self, request, token, *args):

        try:
            session = UploadSession.objects.get(
                token=token
            )
            output = {
                'token': session.token,
                'is_processed': session.is_processed,
                'is_canceled': session.is_canceled
            }
            output.update(session.progress_status())
            return JsonResponse(output)
        except UploadSession.DoesNotExist:
            raise Http404('No session found')
