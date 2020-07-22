import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from gwml2.forms import (
    DrillingAndConstructionForm, GeneralInformationForm,
    GeologyForm, GeologyLogForm, HydrogeologyForm, CasingForm, ScreenForm
)


class GroundwaterFormView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request, 'groundwater_form/main.html',
            {
                'general_information': GeneralInformationForm(),
                'geology': GeologyForm(),
                'drilling_and_construction': DrillingAndConstructionForm(),
                'hydrogeology': HydrogeologyForm(),
                'geology_log': GeologyLogForm(),
                'casing': CasingForm(),
                'screen': ScreenForm(),
            }
        )

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST['data'])
        print(data)
        return HttpResponse('OK')
