from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.models.well_management.user import UserUUID

User = get_user_model()


class UserUUIDAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]
    """
    Return status of the upload session
    """

    def get(self, request, *args):
        try:
            user_uuid = UserUUID.objects.get(user_id=request.user.id)
            if request.user.is_staff:
                try:
                    user_uuid = UserUUID.objects.get(user_id=0)
                except UserUUID.DoesNotExist:
                    pass
            return HttpResponse(user_uuid.uuid)
        except UserUUID.DoesNotExist:
            return Http404('UUID does not exist')


class UserAutocompleteAPI(APIView):
    permission_classes = []
    """
    Return status of the upload session
    """

    def get(self, request, *args):
        return Response([
            {
                'id': user.id,
                'label': user.username
            } for user in User.objects.filter(username__icontains=request.GET.get('q', '-')).exclude(id=-1)
        ])
