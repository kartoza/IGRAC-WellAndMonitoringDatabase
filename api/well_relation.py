__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '20/10/20'

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from braces.views import StaffuserRequiredMixin
from gwml2.models import Well


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
        well = get_object_or_404(Well, id=id)
        queryset = well.relation_queryset(model)
        return HttpResponse(['1'])


class WellRelationDeleteView(StaffuserRequiredMixin, WellRelationAPI):
    def post(self, request, id, model, model_id, *args, **kwargs):
        object = self.get_object(id, model, model_id)
        if not object:
            return Http404('instance is not found')
        object.delete()
        return HttpResponse('OK')
