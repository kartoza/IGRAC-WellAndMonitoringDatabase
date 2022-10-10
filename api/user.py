"""View for User."""
from django.contrib.auth import get_user_model
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication
)
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.models.well_management.user import UserUUID

User = get_user_model()


class UserUUIDAPI(APIView):
    authentication_classes = [
        SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = []
    """
    Return the UUID of user and their extent
    """

    def get(self, request, *args):
        _uuid = 'Not found'
        try:
            user_id = -1
            if request.user.is_authenticated:
                user_id = request.user.id
            _uuid = UserUUID.objects.get(user_id=user_id).uuid
        except UserUUID.DoesNotExist:
            pass
        return Response({
            'uuid': _uuid,
            'extent': (-180.0, -90.0, 180, 90)
        })


class UserAutocompleteAPI(APIView):
    permission_classes = []
    """
    Return the user list 
    """

    def get(self, request, *args):
        return Response([
            {
                'id': user.id,
                'label': user.username
            } for user in User.objects.filter(
                username__icontains=request.GET.get('q', '-')).exclude(id=-1)
        ])
