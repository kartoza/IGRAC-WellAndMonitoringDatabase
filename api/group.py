"""API for group."""

from django.contrib.auth import get_user_model
from geonode.groups.models import GroupProfile
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class GroupAutocompleteAPI(APIView):
    permission_classes = []
    """
    Return group list 
    """

    def get(self, request, *args):
        return Response([
            {
                'id': group.id,
                'label': group.title
            } for group in GroupProfile.objects.filter(
                title__icontains=request.GET.get('q', '')).exclude(id=-1)
        ])
