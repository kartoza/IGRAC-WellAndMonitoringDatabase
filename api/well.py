from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from gwml2.authentication import GWMLTokenAthentication
from gwml2.mixin import EditWellFormMixin
from gwml2.models.well import Well
from gwml2.views.groundwater_form import WellEditing
from rest_framework.views import APIView


class WellEditAPI(WellEditing, APIView, EditWellFormMixin):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, id, *args, **kwargs):
        data = request.data.copy()
        well = get_object_or_404(Well, id=id)

        self.edit_well(well, data, self.request.FILES, request.user)

        return HttpResponse('Updated')
