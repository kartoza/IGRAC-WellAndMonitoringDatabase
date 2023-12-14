__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '20/10/20'

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.models import WellDeletion
from gwml2.serializer.well_deletion import WellDeletionSerializer


class WellDeletionAPI(APIView):
    model = WellDeletion

    permission_classes = (IsAuthenticated,)

    def get(self, request, uuid):
        """Delete an indicator."""
        obj = get_object_or_404(WellDeletion, identifier=uuid)
        return Response(
            WellDeletionSerializer(obj).data
        )
