import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.tasks.download_well import download_well
from gwml2.models.download_session import DownloadSession
from gwml2.utilities import get_organisations_as_viewer


class WellDownloader(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WellDownloader, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Download a well as file
        """
        filters = {}
        orgs = list(get_organisations_as_viewer(self.request.user).values_list('id', flat=True))
        filters.update({
            'organisation': orgs
        })

        try:
            session = DownloadSession.objects.get(filters=filters)
        except DownloadSession.DoesNotExist:
            session = DownloadSession.objects.create(
                filters=filters)
            download_well.delay(request.user.id, session.id, filters)
            request.session['task_id'] = session.token

        output = {
            'task_id': session.token,
            'progress': session.progress
        }
        if session.notes:
            output.update(json.loads(session.notes))

        return JsonResponse(output)

    def post(self, request, *args, **kwargs):
        """
        Download a well as file
        """
        filters = request.data.copy()
        orgs = list(get_organisations_as_viewer(self.request.user).values_list('id', flat=True))
        filters.update({
            'organisation': orgs
        })

        try:
            session = DownloadSession.objects.get(filters=filters)
        except DownloadSession.DoesNotExist:
            session = DownloadSession.objects.create(
                filters=filters)
            download_well.delay(request.user.id, session.id, filters)
            request.session['task_id'] = session.token

        output = {
            'task_id': session.token,
            'progress': session.progress
        }
        if session.notes:
            output.update(json.loads(session.notes))

        return JsonResponse(output)
