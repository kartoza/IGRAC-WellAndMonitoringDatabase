from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.clickjacking import (
    xframe_options_exempt, xframe_options_sameorigin,
)
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameterGroup
from gwml2.models.well import Well
from gwml2.serializer.unit import UnitSerializer

xframe_options_exempt_m = method_decorator(
    xframe_options_exempt, name='dispatch')


class MeasurementChart(View):

    @xframe_options_exempt_m
    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        model = kwargs['model']

        error = ''
        try:
            well = Well.objects.get(id=id)
            if well.editor_permission(request.user) or well.view_permission(request.user):
                pass
            else:
                error = "You don't have permission to access this well."
        except Well.DoesNotExist:
            error = "Well does not found"

        if model != 'WellLevelMeasurement' and model != 'WellQualityMeasurement' and model != 'WellYieldMeasurement':
            error = "Model is not measurements"

        if error:
            return render(
                request,
                'plugins/measurements_chart_error.html',
                {'error': error})

        if model == 'WellLevelMeasurement':
            group_name = 'Level Measurement'
        elif model == 'WellQualityMeasurement':
            group_name = 'Quality Measurement'
        elif model == 'WellYieldMeasurement':
            group_name = 'Yield Measurement'
        else:
            group_name = ''

        parameters = {
            measurement.id: {
                'units': [
                    unit.id for unit in measurement.units.all()],
                'name': measurement.name
            } for measurement in TermMeasurementParameterGroup.objects.get(name=group_name).parameters.all()
        }

        units = {unit.id: UnitSerializer(unit).data for unit in Unit.objects.order_by('id')}

        return render(
            request,
            'plugins/measurements_chart_page.html',
            {
                'id': id,
                'identifier': model,
                'url': reverse('well-level-measurement-chart-data', kwargs={
                    'id': id
                }),
                'top_borehole_elevation': {
                    'u': well.top_borehole_elevation.unit.name if
                    well.top_borehole_elevation and well.top_borehole_elevation.unit else '',
                    'v': well.top_borehole_elevation.value if
                    well.top_borehole_elevation else '',
                },
                'ground_surface_elevation': {
                    'u': well.ground_surface_elevation.unit.name if
                    well.ground_surface_elevation and well.ground_surface_elevation.unit else '',
                    'v': well.ground_surface_elevation.value if
                    well.ground_surface_elevation else '',
                },
                'parameters': parameters,
                'units': units
            }
        )


class MeasurementChartIframe(View):
    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        model = kwargs['model']
        well = get_object_or_404(Well, id=id)

        if model != 'WellLevelMeasurement' and model != 'WellQualityMeasurement' and model != 'WellYieldMeasurement':
            return HttpResponseBadRequest('Model is not measurements')

        return render(
            request,
            'plugins/measurements_chart_iframe.html',
            {
                'url': reverse('well-measurement-chart', kwargs={
                    'id': id,
                    'model': model
                })
            }
        )
