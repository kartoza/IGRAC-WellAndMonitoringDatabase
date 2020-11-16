from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from gwml2.models.well_management.user import UserUUID
from gwml2.authentication import GWMLTokenAthentication


class UserUUIDAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]
    """
    Return status of the upload session
    """

    def get(self, request, *args):
        try:
            user_uuid = UserUUID.objects.get(user_id=request.user.id)
            return HttpResponse(user_uuid.uuid)
        except UserUUID.DoesNotExist:
            return Http404('UUID does not exist')
