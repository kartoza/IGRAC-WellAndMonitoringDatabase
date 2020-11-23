from datetime import datetime
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.mixin import ViewWellFormMixin
from gwml2.models.well import Well
from gwml2.serializer.well.well_information import WellLikeFormSerializer, WellMinimizedSerializer
from gwml2.views.groundwater_form import WellEditing, FormNotValid
from gwml2.utilities import get_organisations_as_viewer


class WellDetailAPI(APIView, ViewWellFormMixin, WellEditing):
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

    def put(self, request, id):
        """
        Update well
        """
        well = get_object_or_404(Well, pk=id)
        data = request.data
        if well.editor_permission(request.user):
            try:
                well = self.edit_well(well, data, self.request.FILES)
            except KeyError as e:
                return HttpResponseBadRequest('{} is needed'.format(e))
            except (ValueError, FormNotValid) as e:
                return HttpResponseBadRequest('{}'.format(e))
            return Response(
                WellLikeFormSerializer(well).data
            )
        else:
            return HttpResponseForbidden('')


class WellListMinimizedAPI(APIView, ViewWellFormMixin, WellEditing):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return Well list in json
        """
        organisations = get_organisations_as_viewer(request.user)
        wells = Well.objects.filter(organisation__in=organisations)
        if request.GET.get('from', None):
            wells = wells.filter(last_edited_at__gte=datetime.fromtimestamp(
                int(request.GET.get('from')))
            )
        if request.GET.get('to', None):
            wells = wells.filter(last_edited_at__lte=datetime.fromtimestamp(
                int(request.GET.get('to')))
            )
        return Response(
            WellMinimizedSerializer(wells, many=True).data
        )
