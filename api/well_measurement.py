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

        STEP = 100
        set = int(request.GET.get('set', 1))
        _from = (set - 1) * STEP
        _to = set * STEP

        queryset = well.relation_queryset(model)

        output = []
        if queryset:
            output = WellMeasurementMinimizedSerializer(queryset.all(), many=True).data
        return JsonResponse({
            'data': output,
            'set': set + 1,
            'end': len(output) < STEP
        })
