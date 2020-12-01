from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import Extent

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.models.well_management.user import UserUUID
from gwml2.models.views.well import WellWithUUID

User = get_user_model()


class UserUUIDAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = []
    """
    Return status of the upload session
    """

    def get(self, request, *args):
        try:
            user_id = -1
            if request.user.is_authenticated:
                user_id = request.user.id
            user_uuid = UserUUID.objects.get(user_id=user_id)
            if request.user.is_staff:
                try:
                    user_uuid = UserUUID.objects.get(user_id=0)
                except UserUUID.DoesNotExist:
                    pass
            wells = WellWithUUID.objects.filter(uuid=user_uuid.uuid).aggregate(Extent('location'))
            return Response({
                'uuid': user_uuid.uuid,
                'extent': wells['location__extent']
            })
        except UserUUID.DoesNotExist:
            return Response({
                'uuid': 'not found',
                'extent': None
            })


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
