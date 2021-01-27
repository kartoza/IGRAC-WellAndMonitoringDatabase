from datetime import datetime
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from geonode.base.models import License, RestrictionCodeType
from gwml2.authentication import GWMLTokenAthentication
from gwml2.models.well import Well
from gwml2.models.term import (
    TermWellStatus, TermWellPurpose, TermFeatureType, TermReferenceElevationType, TermDrillingMethod,
    TermAquiferType, TermConfinement)
from gwml2.models.term_measurement_parameter import TermMeasurementParameterGroup
from gwml2.models.general import UnitGroup
from gwml2.serializer.well.minimized_well import (
    WellMinimizedSerializer,
    WellMeasurementMinimizedSerializer)
from gwml2.utilities import get_organisations_as_viewer, get_organisations_as_editor


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

        if request.GET.get('pks', None):
            wells = wells.filter(id__in=request.GET.get('pks').split(','))

        lat = request.GET.get('lat', None)
        lon = request.GET.get('lon', None)
        if (lat and not lon) or (not lat and lon):
            return HttpResponseBadRequest(
                'Need lat and lon to be able to filter the nearest wells by location')
        elif lat and lon:
            try:
                wells = wells.annotate(
                    distance=Distance(
                        'location', Point(
                            float(lon), float(lat), srid=4326)
                    )
                ).order_by('distance')
            except (TypeError, ValueError):
                return HttpResponseBadRequest(
                    'Lat or lon is not float')

        # check the page
        try:
            page = int(request.GET.get('page', '1'))
            if page < 1:
                return HttpResponseBadRequest('minimal page is 1')
        except ValueError:
            return HttpResponseBadRequest('page must be integer')

        # check the limit
        try:
            limit = int(request.GET.get('limit', '10'))
            if limit < 1:
                return HttpResponseBadRequest('minimal limit is 1')
        except ValueError:
            return HttpResponseBadRequest('minimal must be integer')

        idx_start = (page - 1) * limit
        idx_end = idx_start + limit
        total_count = wells.count()
        wells = wells[idx_start:idx_end]
        count = wells.count()

        # put terms in the output
        terms = {}
        for Model in [TermWellStatus, TermWellPurpose, TermFeatureType, License,
                      RestrictionCodeType, TermReferenceElevationType, TermDrillingMethod,
                      TermAquiferType, TermConfinement]:
            terms[Model._meta.model_name] = [{
                model.id: getattr(model, 'name', None) if getattr(model, 'name', None) else model.__str__()
            } for model in Model.objects.all()]

        units = {}
        for group in UnitGroup.objects.all():
            try:
                units[group.name] = [model.name for model in group.units.all()]
            except UnitGroup.DoesNotExist:
                units[group.name] = []
        terms['units'] = units

        measurement_parameters = {}
        for group in TermMeasurementParameterGroup.objects.all():
            measurement_parameters[group.name] = {}
            for parameters in group.parameters.all():
                measurement_parameters[group.name][parameters.name] = [
                    unit.name for unit in parameters.units.all()
                ]
        terms['measurement_parameters'] = measurement_parameters
        terms['organisation'] = [{org.id: org.name} for org in get_organisations_as_editor(request.user)]

        url = request.build_absolute_uri().split('?')[0]
        next = ''
        if page * limit < total_count:
            params = request.GET.copy()
            params['page'] = page + 1
            next = '{}?{}'.format(
                url, '&'.join(['{}={}'.format(key, value) for key, value in params.items()])
            )

        previous = ''
        if page > 1:
            params = request.GET.copy()
            params['page'] = page - 1
            previous = '{}?{}'.format(
                url, '&'.join(['{}={}'.format(key, value) for key, value in params.items()])
            )

        return Response(
            {
                'count': total_count,
                'next': next,
                'previous': previous,
                'terms': terms,
                'results': WellMinimizedSerializer(wells, many=True, context={'user': request.user}).data
            })


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

        # check the limit
        try:
            limit = int(request.GET.get('limit', '10'))
            if limit < 1:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest('minimal limit is 1')

        idx_start = (page - 1) * limit
        idx_end = idx_start + limit

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
