from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404, HttpResponse
from django.views.generic.base import View
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from gwml2.api.pagination import Pagination
from gwml2.models.upload_session import UploadSession
from gwml2.serializer.upload_session import UploadSessionSerializer


class UploadSessionListApiView(ListAPIView):
    """Return List of upload session."""

    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination
    serializer_class = UploadSessionSerializer

    def get_queryset(self):
        """Return queryset of API."""
        return UploadSession.objects.filter(
            uploader=self.request.user.id
        )


class UploadSessionApiView(View):
    """
    Return status of the upload session
    """

    def get(self, request, token, *args):

        try:
            session = UploadSession.objects.get(token=token)
            output = UploadSessionSerializer(session).data
            output.update(session.progress_status())
            return JsonResponse(output)
        except UploadSession.DoesNotExist:
            raise Http404('No session found')

    def post(self, request, token, *args):
        """Resume the upload."""
        try:
            session = UploadSession.objects.get(token=token)
            if not session.uploader:
                raise PermissionDenied()
            if request.user.id != session.uploader:
                raise PermissionDenied()
            session.is_canceled = False
            session.save()
            session.run_in_background()
            return HttpResponse('ok')
        except UploadSession.DoesNotExist:
            raise Http404('No session found')

    def delete(self, request, token, *args):
        """Resume the upload."""
        try:
            session = UploadSession.objects.get(token=token)
            if not session.uploader:
                raise PermissionDenied()
            if request.user.id != session.uploader:
                raise PermissionDenied()
            session.delete()
            return HttpResponse('ok')
        except UploadSession.DoesNotExist:
            raise Http404('No session found')


class UploadSessionStopApiView(View):
    """Stop an upload."""

    def post(self, request, token, *args):
        """Resume the upload."""
        try:
            session = UploadSession.objects.get(token=token)
            if not session.uploader:
                raise PermissionDenied()
            if request.user.id != session.uploader:
                raise PermissionDenied()
            session.is_canceled = True
            session.save()
            return HttpResponse('ok')
        except UploadSession.DoesNotExist:
            raise Http404('No session found')
