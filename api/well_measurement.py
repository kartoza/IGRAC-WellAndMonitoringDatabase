import datetime
from datetime import timedelta
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from gwml2.models import Well
from gwml2.serializer.well.minimized_well import WellMeasurementMinimizedSerializer


class WellMeasurements(APIView):
    def get(self, request, id, model, *args, **kwargs):
        if model != 'WellLevelMeasurement' and model != 'WellQualityMeasurement' and model != 'WellYieldMeasurement':
            return HttpResponseBadRequest('Model is not measurements')

        well = get_object_or_404(Well, id=id)
        if not well.view_permission(request.user):
            return HttpResponseForbidden('')

        queryset = well.relation_queryset(model)
        if not queryset:
            return HttpResponseBadRequest('Model is not recognized')
        queryset = queryset.all()

        # check page
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            return HttpResponseBadRequest('Page is not integer')

        # check per timerange
        timerange = request.GET.get('timerange', 0)
        today = datetime.datetime.today()

        if timerange == 'hourly':
            # hourly
            STEP = 100
            _from = (page - 1) * STEP
            _to = page * STEP
            queryset = queryset[_from:_to]
        elif timerange == 'daily':
            # hourly
            STEP = 100
            _from = today - timedelta(days=(page - 1) * STEP)
            _to = today - timedelta(days=STEP)
            queryset = queryset.filter(time__gt=_from, time__lte=_from)
        else:
            return HttpResponseBadRequest('Timerange is not recognizes')

        output = WellMeasurementMinimizedSerializer(queryset, many=True).data
        return JsonResponse({
            'data': output,
            'page': page + 1,
            'end': len(output) < STEP
        })
