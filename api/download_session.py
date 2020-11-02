import json
from django.http import JsonResponse, Http404
from django.views.generic.base import View
from gwml2.models.download_session import DownloadSession


class DownloadSessionApiView(View):
    """
    Return status of the download session
    """

    def get(self, request, token, *args):
        try:
            session = DownloadSession.objects.get(
                token=token
            )
        except DownloadSession.DoesNotExist:
            raise Http404('No session found')
        output = {
            'task_id': session.token,
            'progress': session.progress
        }
        if session.notes:
            output.update(json.loads(session.notes))

        return JsonResponse(output)
