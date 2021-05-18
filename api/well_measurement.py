import datetime
from datetime import timedelta
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from gwml2.models import Well
from gwml2.models.general import Unit
from gwml2.serializer.unit import UnitWithToSerializer

MEASUREMENT_PARAMETER_AMSL = 'Water level elevation a.m.s.l.'
MEASUREMENT_PARAMETER_TOP = 'Water depth [from the top of the well]'
MEASUREMENT_PARAMETER_GROUND = 'Water depth [from the ground surface]'

MEASUREMENT_YEARLY_MODE = 'yearly'
MEASUREMENT_WEEKLY_MODE = 'weekly'
MEASUREMENT_MONTHLY_MODE = 'monthly'
MEASUREMENT_DAILY_MODE = 'daily'


class WellLevelMeasurementData(APIView):
    def convert_value(self, quantity, unit_to, units):
        """ Get value of quantity
        convert to unit_to
        """
        # let's we change the data
        value = quantity.value
        if quantity.unit and quantity.unit.id != unit_to:
            try:
                formula = units[quantity.unit.id]['to'][unit_to]
                value = eval(formula.replace('x', '{}'.format(value)))
            except KeyError:
                pass
        return value

    def get(self, request, id, *args, **kwargs):
        well = get_object_or_404(Well, id=id)
        if not well.view_permission(request.user):
            return HttpResponseForbidden('')

        queryset = well.relation_queryset('WellLevelMeasurement')
        if not queryset:
            return HttpResponseBadRequest('Model is not recognized')
        queryset = queryset.all()

        # check mode
        try:
            mode = request.GET['mode']
        except KeyError:
            return HttpResponseBadRequest('Parameter : mode is required')
        today = datetime.datetime.today()

        if mode == MEASUREMENT_DAILY_MODE:
            _to = today
            _from = _to - timedelta(days=100)
            queryset = queryset.filter(time__gt=_from, time__lte=_to)
        elif mode == MEASUREMENT_WEEKLY_MODE:
            _to = today
            _from = _to.replace(year=_to.year - 1)
            queryset = queryset.filter(time__gt=_from, time__lte=_to)
        elif mode == MEASUREMENT_MONTHLY_MODE:
            _to = today
            _from = _to.replace(year=_to.year - 10)
            queryset = queryset.filter(time__gt=_from, time__lte=_to)
        elif mode == MEASUREMENT_YEARLY_MODE:
            queryset = queryset
        else:
            return HttpResponseBadRequest('Timerange is not recognized')

        units = {unit.id: UnitWithToSerializer(unit).data for unit in Unit.objects.all()}
        unit_to = None
        unit_to_str = None
        ground_surface_elevation = well.ground_surface_elevation
        if ground_surface_elevation:
            unit_to = ground_surface_elevation.unit.id
            unit_to_str = ground_surface_elevation.unit.name
            ground_surface_elevation = ground_surface_elevation.value
        top_borehole_elevation = well.top_borehole_elevation
        if top_borehole_elevation:
            if not unit_to:
                unit_to = top_borehole_elevation.unit.id
                unit_to_str = top_borehole_elevation.unit.name
            top_borehole_elevation = self.convert_value(
                top_borehole_elevation, unit_to, units)

        # create aggregation
        aggr = {}
        for measurement in queryset:
            identifier = None
            if measurement.value and measurement.value.value:
                if mode == MEASUREMENT_DAILY_MODE:
                    identifier = measurement.time.strftime("%Y-%m-%d")
                elif mode == MEASUREMENT_WEEKLY_MODE:
                    calendar = measurement.time.isocalendar()
                    identifier = '{} Week {}'.format(calendar[0], ('{}'.format(calendar[1])).zfill(2))
                elif mode == MEASUREMENT_MONTHLY_MODE:
                    identifier = '{}'.format(measurement.time.strftime('%Y %B'))
                elif mode == MEASUREMENT_YEARLY_MODE:
                    identifier = '{}'.format(measurement.time.strftime('%Y'))
            if identifier:
                # convert the data
                value = self.convert_value(measurement.value, unit_to, units)
                parameter = MEASUREMENT_PARAMETER_AMSL
                if measurement.parameter.name == MEASUREMENT_PARAMETER_TOP:
                    if top_borehole_elevation:
                        value = top_borehole_elevation - value
                    else:
                        parameter = measurement.parameter.name
                elif measurement.parameter.name == MEASUREMENT_PARAMETER_GROUND:
                    if ground_surface_elevation:
                        value = ground_surface_elevation - value
                    else:
                        parameter = measurement.parameter.name

                # save it to aggregation
                if value:
                    if identifier not in aggr:
                        aggr[identifier] = {}
                    if parameter not in aggr[identifier]:
                        aggr[identifier][parameter] = []
                    aggr[identifier][parameter].append(value)

        output = []
        for key, value in aggr.items():
            for param, data in value.items():
                data = sorted(data)
                length = len(data)
                if length > 0:
                    index = (length - 1) // 2

                    if length % 2:
                        median = data[index]
                    else:
                        median = (data[index] + data[index + 1]) / 2.0
                    output.append({
                        'dt': key,
                        'par': param,
                        'u': unit_to_str,
                        'v': {
                            'min': min(data),
                            'max': max(data),
                            'avg': sum(data) / length,
                            'med': median,
                        }
                    })
        return JsonResponse({
            'data': output,
            'page': 1,
            'end': True
        })
