from django.db.models import Case, When, Value, IntegerField
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import (
    xframe_options_exempt, )
from django.views.generic import View

from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup
)
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
        except Well.DoesNotExist:
            error = "Well does not found"

        if model != 'WellLevelMeasurement' and model != 'WellQualityMeasurement' and model != 'WellYieldMeasurement' and model != 'WellMeasurement':
            error = "Model is not measurements"

        if error:
            return render(
                request,
                'plugins/measurements_chart_error.html',
                {'error': error})

        groups = {}
        if model == 'WellLevelMeasurement' or model == 'WellMeasurement':
            group_name = 'Level Measurement'
            groups[group_name] = 'Groundwater Level'
        if model == 'WellQualityMeasurement' or model == 'WellMeasurement':
            group_name = 'Quality Measurement'
            groups[group_name] = 'Groundwater Quality'
        if model == 'WellYieldMeasurement' or model == 'WellMeasurement':
            group_name = 'Yield Measurement'
            groups[group_name] = 'Groundwater Yield'

        parameters = {}
        for group_name, group_header in groups.items():
            parameters[group_header] = {
                measurement.id: {
                    'units': [
                        unit.id for unit in measurement.units.annotate(
                            custom_order=Case(
                                When(name='m', then=Value(1)),
                                When(name='ft', then=Value(2)),
                                When(name='cm', then=Value(3)),
                                default=Value(99),
                                output_field=IntegerField(),
                            )
                        ).order_by('custom_order')],
                    'name': measurement.name
                } for measurement in TermMeasurementParameterGroup.objects.get(
                    name=group_name).parameters.all()
            }

        units = {
            unit.id: UnitSerializer(unit).data for unit in
            Unit.objects.order_by('id')
        }

        # Return data url
        urls = [
            reverse('well-measurement-chart-data', kwargs={
                'id': id,
                'model': model
            })
        ]
        if model == 'WellMeasurement':
            urls = [
                reverse('well-measurement-chart-data', kwargs={
                    'id': id,
                    'model': model
                })
                for model in [
                    'WellLevelMeasurement', 'WellQualityMeasurement',
                    'WellYieldMeasurement'
                ]]
        return render(
            request,
            'plugins/measurements_chart_page.html',
            {
                'id': id,
                'identifier': model,
                'urls': urls,
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
