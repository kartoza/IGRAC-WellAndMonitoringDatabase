from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from gwml2.authentication import GWMLTokenAthentication
from gwml2.serializer.well.minimized_well import WellMinimizedSerializer
from gwml2.mixin import EditWellFormMixin
from gwml2.models.well import Well
from gwml2.views.form_group.form_group import FormNotValid
from gwml2.views.groundwater_form import WellEditing


class WellCreateMinimizedAPI(WellEditing, APIView, EditWellFormMixin):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        try:
            well = self.edit_well(None, data, self.request.FILES, request.user)
            return JsonResponse(WellMinimizedSerializer(well, context={'user': request.user}).data)

        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid, Exception) as e:
            return HttpResponseBadRequest('{}'.format(e))


class WellEditMinimizedAPI(WellEditing, APIView, EditWellFormMixin):
    authentication_classes = [SessionAuthentication, BasicAuthentication, GWMLTokenAthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, id, *args, **kwargs):
        data = request.data.copy()
        well = get_object_or_404(Well, id=id)

        try:
            well = self.edit_well(well, data, self.request.FILES, request.user)
            return JsonResponse(WellMinimizedSerializer(well, context={'user': request.user}).data)

        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid, Exception) as e:
            return HttpResponseBadRequest('{}'.format(e))
