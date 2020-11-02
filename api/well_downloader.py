import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from gwml2.tasks.download_well import download_well
from gwml2.models.download_session import DownloadSession


class WellDownloader(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WellDownloader, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Download a well as file
        """
        filters = json.loads(request.body)

        try:
            session = DownloadSession.objects.get(filters=filters)
        except DownloadSession.DoesNotExist:
            session = DownloadSession.objects.create(
                filters=filters)
            download_well.delay(session.id, filters)
            request.session['task_id'] = session.token

        output = {
            'task_id': session.token,
            'progress': session.progress
        }
        if session.notes:
            output.update(json.loads(session.notes))

        return JsonResponse(output)
