import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import View
from gwml2.forms import (
    # DrillingAndConstructionForm,
    GeneralInformationForm,
    GeologyForm,
    # HydrogeologyForm,
    ManagementForm, LicenseForm, GeologyLogForm,
    # CasingForm, ScreenForm,
    DocumentForm,
    # OrganisationForm, ReferenceElevationForm, MeasurementForm,
    # WaterStrikeForm
)
from gwml2.models.geology import Geology, GeologyLog
from gwml2.models.management import Management, License
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

        geology_logs = []
        if well.geology:
            for geology_log in well.geology.geologylog_set.all():
                geology_logs.append(GeologyLogForm.make_from_instance(geology_log))
        return render(
            request, 'groundwater_form/main.html',
            {
                # general_information
                'general_information': GeneralInformationForm.make_from_instance(well),
                'document': DocumentForm(),  # manytomany form
                'documents': documents,  # manytomany data

                # # geology
                'geology': GeologyForm.make_from_instance(well.geology),
                'geology_log': GeologyLogForm(),
                'geology_logs': geology_logs,
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
                # management
                'management': ManagementForm.make_from_instance(well.management),
                'license': LicenseForm.make_from_instance(well.management.license if well.management else None),
                #
                # # monitoring data
                # 'measurement': MeasurementForm(),
            }
        )

    def make_form(self, instance, form, data):
        """ make form from data

        :rtype: ModelForm
        """
        form = form.make_from_data(
            instance, data, self.request.FILES)
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

            # -----------------------------------------
            # documents
            # -----------------------------------------
            documents = []
            for document in data['documents']:
                well_doc = WellDocument.objects.get(
                    id=document['id_doc']) if document['id_doc'] else WellDocument()
                if not well_doc.well_id:
                    well_doc.well = well

                documents.append(
                    self.make_form(well_doc, DocumentForm, document)
                )

            # -----------------------------------------
            # geology and geology logs
            # -----------------------------------------
            geology = well.geology if well.geology else Geology()
            geology_form = self.make_form(
                geology, GeologyForm, data['geology'])

            geology_logs = []
            for log in data['geology']['geology_log']:
                geo_log = GeologyLog.objects.get(
                    id=log['id_log']) if log['id_log'] else GeologyLog()

                geology_logs.append(
                    self.make_form(
                        geo_log, GeologyLogForm, log
                    )
                )

            # -----------------------------------------
            # management
            # -----------------------------------------
            management = well.management if well.management else Management()
            management_form = self.make_form(
                management, ManagementForm, data['management'])

            license = management.license if well.management else License()
            license_form = self.make_form(
                license, LicenseForm, data['management']['license']
            )

            # -----------------------------------------
            # save all forms
            # -----------------------------------------
            geology_form.save()
            for log in geology_logs:
                log.instance.geology = geology_form.instance
                log.save()

            license_form.save()
            management.license = license_form.instance
            management_form.save()

            for document in documents:
                document.save()
            well.geology = geology_form.instance
            well.management = management
            general_information.save()
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse('OK')
