import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from gwml2.forms import (
    DrillingAndConstructionForm, GeneralInformationForm,
    GeologyForm, HydrogeologyForm, ManagementForm,
    GeologyLogForm, CasingForm, ScreenForm, DocumentForm,
    OrganisationForm, LicenseForm
)


class GroundwaterFormView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request, 'groundwater_form/main.html',
            {
                # general_information
                'general_information': GeneralInformationForm(),
                'document': DocumentForm(),

                # geology
                'geology': GeologyForm(),
                'geology_log': GeologyLogForm(),

                # drilling_and_construction
                'drilling_and_construction': DrillingAndConstructionForm(),
                'casing': CasingForm(),
                'screen': ScreenForm(),

                # hydrogeology
                'hydrogeology': HydrogeologyForm(),

                # management
                'management': ManagementForm(),
                'organisation': OrganisationForm(),
                'license': LicenseForm(),
            }
        )

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST['data'])
        print(data)
        return HttpResponse('OK')
