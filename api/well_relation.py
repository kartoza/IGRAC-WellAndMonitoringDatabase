__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '20/10/20'

import os
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from braces.views import StaffuserRequiredMixin
from gwml2.models import Well
from gwml2.forms import get_form_from_model
from gwml2.templatetags.gwml2_forms import delete_url


class WellRelationAPI(View):

    def get_object(self, id, model, model_id):
        """ Return object of relation based on well id, model and model id
        """
        well = get_object_or_404(Well, id=id)
        queryset = well.relation_queryset(model)
        if queryset:
            return get_object_or_404(queryset, id=model_id)
        else:
            return None


class WellRelationListView(View):
    def get(self, request, id, model, *args, **kwargs):
        """ Return list object based on well id and model name
        """
        STEP = 10
        set = int(request.GET.get('set', 1))
        _from = (set - 1) * STEP
        _to = set * STEP

        well = get_object_or_404(Well, id=id)
        queryset = well.relation_queryset(model)
        output = []
        if queryset:
            Form = get_form_from_model(model)
            for obj in queryset.all()[_from:_to]:
                form = Form.make_from_instance(obj)
                output.append({
                    'html': form.as_p(),
                    'delete_url': delete_url(well, obj)
                })
        return JsonResponse({
            'data': output,
            'set': set + 1,
            'end': len(output) < STEP
        })


class WellMeasurementDataView(View):
    def get(self, request, id, model, *args, **kwargs):
        """ Return data of measurement
        """
        well = get_object_or_404(Well, id=id)
        cache_file = well.return_measurement_cache_path(model)
        if os.path.exists(cache_file):
            _file = open(cache_file, "rb")
            compressed_content = _file.read()
            response = HttpResponse(compressed_content)
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = str(len(compressed_content))
            return response
        else:
            return HttpResponseBadRequest('Model is not recognized')


class WellRelationDeleteView(StaffuserRequiredMixin, WellRelationAPI):
    def post(self, request, id, model, model_id, *args, **kwargs):
        object = self.get_object(id, model, model_id)
        if not object:
            return Http404('instance is not found')
        object.delete()
        return HttpResponse('OK')
