import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import View
from gwml2.forms import (
    DrillingAndConstructionForm,
    GeneralInformationForm,
    GeologyForm,
    HydrogeologyParameterForm,
    PumpingTestForm,
    ManagementForm, LicenseForm, GeologyLogForm,
    CasingForm, ScreenForm, WaterStrikeForm,
    DocumentForm,
    # OrganisationForm, ReferenceElevationForm,
    MeasurementForm

)
from gwml2.models.drilling_and_construction import (
    DrillingAndConstruction, Casing, Screen, WaterStrike
)
from gwml2.models.geology import Geology, GeologyLog
from gwml2.models.hydrogeology import HydrogeologyParameter, PumpingTest
from gwml2.models.management import Management, License
from gwml2.models.well import Well, WellDocument, WellMeasurement


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

        measurements = []
        for measurement in well.wellmeasurement_set.all():
            measurements.append(MeasurementForm.make_from_instance(measurement))

        casings = []
        screens = []
        water_strikes = []
        if well.drilling_and_construction:
            for obj in well.drilling_and_construction.casing_set.all():
                casings.append(CasingForm.make_from_instance(obj))
            for obj in well.drilling_and_construction.screen_set.all():
                screens.append(ScreenForm.make_from_instance(obj))
            for obj in well.drilling_and_construction.waterstrike_set.all():
                water_strikes.append(WaterStrikeForm.make_from_instance(obj))

        return render(
            request, 'groundwater_form/main.html',
            {
                # general_information
                'general_information': GeneralInformationForm.make_from_instance(well),
                'document': DocumentForm(),  # manytomany form
                'documents': documents,  # manytomany data

                # geology
                'geology': GeologyForm.make_from_instance(well.geology),
                'geology_log': GeologyLogForm(),
                'geology_logs': geology_logs,

                # drilling_and_construction
                'drilling_and_construction': DrillingAndConstructionForm.make_from_instance(
                    well.drilling_and_construction),
                'casing': CasingForm(),
                'casings': casings,
                'screen': ScreenForm(),
                'screens': screens,
                'water_strike': WaterStrikeForm(),
                'water_strikes': water_strikes,

                # hydrogeology
                'hydrogeology': HydrogeologyParameterForm.make_from_instance(
                    well.hydrogeology_parameter),
                'pumping_test': PumpingTestForm.make_from_instance(
                    well.hydrogeology_parameter.pumping_test
                    if well.hydrogeology_parameter else None),

                # management
                'management': ManagementForm.make_from_instance(well.management),
                'license': LicenseForm.make_from_instance(
                    well.management.license if well.management else None),

                # monitoring data
                'measurement': MeasurementForm(),
                'measurements': measurements
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
                    id=log['id_']) if log['id_'] else GeologyLog()

                geology_logs.append(
                    self.make_form(
                        geo_log, GeologyLogForm, log
                    )
                )
            # -----------------------------------------
            # drilling and construction
            # -----------------------------------------
            drilling_and_construction = well.drilling_and_construction \
                if well.drilling_and_construction else DrillingAndConstruction()
            drilling_and_construction_form = self.make_form(
                drilling_and_construction, DrillingAndConstructionForm, data['drilling_and_construction'])

            casings = []
            for casing in data['drilling_and_construction']['casing']:
                obj = Casing.objects.get(
                    id=casing['id_']) if casing['id_'] else Casing()

                casings.append(
                    self.make_form(
                        obj, CasingForm, casing
                    )
                )
            screens = []
            for screen in data['drilling_and_construction']['screen']:
                obj = Screen.objects.get(
                    id=screen['id_']) if screen['id_'] else Screen()

                screens.append(
                    self.make_form(
                        obj, ScreenForm, screen
                    )
                )
            water_strikes = []
            for water_strike in data['drilling_and_construction']['water_strike']:
                obj = WaterStrike.objects.get(
                    id=water_strike['id_']) if water_strike['id_'] else WaterStrike()

                water_strikes.append(
                    self.make_form(
                        obj, WaterStrikeForm, water_strike
                    )
                )

            # -----------------------------------------
            # hydrogeology
            # -----------------------------------------
            hydrogeo = well.hydrogeology_parameter if well.hydrogeology_parameter else HydrogeologyParameter()
            hydrogeo_form = self.make_form(
                hydrogeo, HydrogeologyParameterForm, data['hydrogeology'])

            pumping_test = hydrogeo.pumping_test if hydrogeo.pumping_test else PumpingTest()
            pumping_test_form = self.make_form(
                pumping_test, PumpingTestForm, data['hydrogeology']['pumping_test']
            )

            # -----------------------------------------
            # management
            # -----------------------------------------
            management = well.management if well.management else Management()
            management_form = self.make_form(
                management, ManagementForm, data['management'])

            license = management.license if management.license else License()
            license_form = self.make_form(
                license, LicenseForm, data['management']['license']
            )

            # -----------------------------------------
            # measurements
            # -----------------------------------------
            measurements = []
            for measurement in data['monitoring_data']['measurement']:
                obj = WellMeasurement.objects.get(
                    id=measurement['id_']) if measurement['id_'] else WellMeasurement()
                if not obj.well_id:
                    obj.well = well

                measurements.append(
                    self.make_form(obj, MeasurementForm, measurement)
                )
            # -----------------------------------------
            # save all forms
            # -----------------------------------------
            drilling_and_construction_form.save()
            for casing in casings:
                casing.instance.drilling_and_construction = drilling_and_construction_form.instance
                casing.save()
            for screen in screens:
                screen.instance.drilling_and_construction = drilling_and_construction_form.instance
                screen.save()
            for water_strike in water_strikes:
                water_strike.instance.drilling_and_construction = drilling_and_construction_form.instance
                water_strike.save()

            geology_form.save()
            for log in geology_logs:
                log.instance.geology = geology_form.instance
                log.save()

            pumping_test_form.save()
            hydrogeo.pumping_test = pumping_test_form.instance
            hydrogeo_form.save()

            license_form.save()
            management.license = license_form.instance
            management_form.save()

            well.drilling_and_construction = drilling_and_construction_form.instance
            well.geology = geology_form.instance
            well.hydrogeology_parameter = hydrogeo_form.instance
            well.management = management
            general_information.save()

            for document in documents:
                document.save()

            for measurement in measurements:
                measurement.save()
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse('OK')
