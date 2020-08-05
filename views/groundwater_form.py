import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import View
from gwml2.forms import (
    # DrillingAndConstructionForm,
    GeneralInformationForm,
    # GeologyForm, HydrogeologyForm, ManagementForm,
    # GeologyLogForm, CasingForm, ScreenForm,
    DocumentForm,
    # OrganisationForm, LicenseForm, ReferenceElevationForm, MeasurementForm,
    # WaterStrikeForm
)
from gwml2.models.well import Well, WellDocument


class FormNotValid(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class WellFormView(StaffuserRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        well = get_object_or_404(Well, id=id)
        documents = []
        for document in well.welldocument_set.all():
            documents.append(DocumentForm.make_from_instance(document))
        return render(
            request, 'groundwater_form/main.html',
            {
                # general_information
                'general_information': GeneralInformationForm.make_from_instance(well),
                'document': DocumentForm(),  # manytomany form
                'documents': documents,  # manytomany data

                # # geology
                # 'geology': GeologyForm(),
                # 'reference_elevation': ReferenceElevationForm(),
                # 'geology_log': GeologyLogForm(),
                #
                # # drilling_and_construction
                # 'drilling_and_construction': DrillingAndConstructionForm(),
                # 'casing': CasingForm(),
                # 'screen': ScreenForm(),
                # 'water_strike': WaterStrikeForm(),
                #
                # # hydrogeology
                # 'hydrogeology': HydrogeologyForm(),
                #
                # # management
                # 'management': ManagementForm(),
                # 'organisation': OrganisationForm(),
                # 'license': LicenseForm(),
                #
                # # monitoring data
                # 'measurement': MeasurementForm(),
            }
        )

    def make_form(self, well, form, data):
        """ make form from data

        :rtype: ModelForm
        """
        form = form.make_from_data(
            well, data, self.request.FILES)
        if not form.is_valid():
            raise FormNotValid(json.dumps(form.errors))
        return form

    def post(self, request, id, *args, **kwargs):
        data = json.loads(request.POST['data'])
        well = get_object_or_404(Well, id=id)

        try:
            # general information
            general_information = self.make_form(
                well, GeneralInformationForm, data['general_information'])

            # documents
            documents = []
            for document in data['documents']:
                well_doc = WellDocument.objects.get(
                    id=document['id_doc']) if document['id_doc'] else WellDocument()
                if not well_doc.well_id:
                    well_doc.well = well

                documents.append(
                    self.make_form(
                        well_doc, DocumentForm, document
                    )
                )
            for document in documents:
                document.save()

            general_information.save()
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse('OK')
