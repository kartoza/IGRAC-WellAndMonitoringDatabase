from datetime import datetime
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.models.well import Well
from gwml2.serializer.well.minimized_well import (
    WellMinimizedSerializer,
    WellMeasurementMinimizedSerializer)
from gwml2.utilities import get_organisations_as_viewer


class WellListMinimizedAPI(APIView):
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
        # check the page
        try:
            page = int(request.GET.get('page', '1'))
            if page < 1:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest('minimal page is 1')

        # check the offset
        try:
            offset = int(request.GET.get('offset', '10'))
            if offset < 1:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest('minimal offset is 1')

        idx_start = (page - 1) * offset
        idx_end = idx_start + offset - 1
        wells = wells[idx_start:idx_end]

        return Response(
            WellMinimizedSerializer(wells, many=True).data
        )


class WellMeasurementListMinimizedAPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id, measurement_type):
        """
        Return Well measurement list in json
        """
        well = get_object_or_404(Well, pk=id)

        # check the page
        try:
            page = int(request.GET.get('page', '1'))
            if page < 1:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest('minimal page is 1')

        # check the offset
        try:
            offset = int(request.GET.get('offset', '10'))
            if offset < 1:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest('minimal offset is 1')

        idx_start = (page - 1) * offset
        idx_end = idx_start + offset - 1

        if well.view_permission(request.user):
            query = None
            if measurement_type == 'level':
                """ return level of measurement"""
                query = well.welllevelmeasurement_set.all()
            elif measurement_type == 'quality':
                """ return quality of measurement"""
                query = well.wellqualitymeasurement_set.all()
            elif measurement_type == 'yield':
                """ return level of measurement"""
                query = well.wellyieldmeasurement_set.all()
            if query:
                return Response(
                    WellMeasurementMinimizedSerializer(
                        query[idx_start:idx_end], many=True).data)
            else:
                return HttpResponseBadRequest('the measurement type parameters are : level, quality or yield')
        else:
            return HttpResponseForbidden('')
