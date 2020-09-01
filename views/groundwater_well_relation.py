__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '01/09/20'

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from braces.views import StaffuserRequiredMixin
from gwml2.models.well import Well, WellDocument


class WellRelationView(StaffuserRequiredMixin, View):
    def post(self, request, id, model, model_id, *args, **kwargs):
        well = get_object_or_404(Well, id=id)
        try:
            if model == 'WellDocument':
                well.welldocument_set.get(id=model_id).delete()
        except WellDocument.DoesNotExist:
            return Http404('instance is not found')
        return HttpResponse('OK')
