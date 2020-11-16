from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.mixin import ViewWellFormMixin
from gwml2.models.well import Well
from gwml2.serializer.well.well_information import WellLikeFormSerializer


class WellDetailAPI(APIView, ViewWellFormMixin):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """
        Return Well Detail in geojson
        """
        well = get_object_or_404(Well, pk=id)
        if well.view_permission(request.user):
            return Response(
                WellLikeFormSerializer(well).data
            )
        else:
            return HttpResponseForbidden('')
