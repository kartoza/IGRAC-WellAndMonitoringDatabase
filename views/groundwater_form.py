import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import View
from gwml2.forms import (
    GeneralInformationForm,
    ConstructionForm, DrillingForm,
    HydrogeologyParameterForm,
    PumpingTestForm,
    ManagementForm, LicenseForm, StratigraphicLogForm,
    CasingForm, ScreenForm, WaterStrikeForm,
    DocumentForm,
    ReferenceElevationForm,
    WellGroundwaterLevelMeasurementForm,
    WellYieldMeasurementForm,
    WellQualityMeasurementForm

)
from gwml2.models.construction import (
    Construction, Casing, Screen
)
from gwml2.models.drilling import (
    Drilling, StratigraphicLog, WaterStrike
)
from gwml2.models.hydrogeology import HydrogeologyParameter, PumpingTest
from gwml2.models.management import Management, License
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.models.well import (
    Well, WellDocument,
    WellGroundwaterLevelMeasurement, WellYieldMeasurement, WellQualityMeasurement
)


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

        # monitoring data
        level_measurements = []
        if well.groundwater_level:
            for measurement in well.groundwater_level.wellgroundwaterlevelmeasurement_set.all():
                level_measurements.append(WellGroundwaterLevelMeasurementForm.make_from_instance(
                    measurement))
        yield_measurements = []
        for measurement in well.wellyieldmeasurement_set.all():
            yield_measurements.append(WellYieldMeasurementForm.make_from_instance(
                measurement))
        quality_measurements = []
        for measurement in well.wellqualitymeasurement_set.all():
            quality_measurements.append(WellQualityMeasurementForm.make_from_instance(
                measurement))

        # drilling
        water_strikes = []
        stratigraphic_logs = []
        if well.drilling:
            for obj in well.drilling.waterstrike_set.all():
                water_strikes.append(WaterStrikeForm.make_from_instance(obj))
            for obj in well.drilling.stratigraphiclog_set.all():
                stratigraphic_logs.append(StratigraphicLogForm.make_from_instance(obj))

        # construction
        casings = []
        screens = []
        if well.construction:
            for obj in well.construction.casing_set.all():
                casings.append(CasingForm.make_from_instance(obj))
            for obj in well.construction.screen_set.all():
                screens.append(ScreenForm.make_from_instance(obj))
        return render(
            request, 'groundwater_form/main.html',
            {
                # general_information
                'general_information': GeneralInformationForm.make_from_instance(well),
                'document': DocumentForm(),  # manytomany form
                'documents': documents,  # manytomany data

                # drilling
                'drilling': DrillingForm.make_from_instance(
                    well.drilling),
                'water_strike': WaterStrikeForm(),
                'water_strikes': water_strikes,
                'stratigraphic_log': StratigraphicLogForm(),
                'stratigraphic_logs': stratigraphic_logs,
                'drilling_elevation': ReferenceElevationForm.make_from_instance(
                    well.drilling.reference_elevation
                    if well.drilling else None),

                # construction
                'construction': ConstructionForm.make_from_instance(
                    well.construction),
                'casing': CasingForm(),
                'casings': casings,
                'screen': ScreenForm(),
                'screens': screens,
                'construction_elevation': ReferenceElevationForm.make_from_instance(
                    well.construction.reference_elevation
                    if well.construction else None),

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
                'level_measurement': WellGroundwaterLevelMeasurementForm(),
                'level_measurements': level_measurements,
                'yield_measurement': WellYieldMeasurementForm(),
                'yield_measurements': yield_measurements,
                'quality_measurement': WellQualityMeasurementForm(),
                'quality_measurements': quality_measurements
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
            # drilling
            # -----------------------------------------
            drilling = well.drilling \
                if well.drilling else Drilling()
            drilling_form = self.make_form(
                drilling, DrillingForm, data['drilling'])

            stratigraphic_log = []
            for log in data['drilling']['stratigraphic_log']:
                obj = StratigraphicLog.objects.get(
                    id=log['id_']) if log['id_'] else StratigraphicLog()

                stratigraphic_log.append(
                    self.make_form(
                        obj, StratigraphicLogForm, log
                    )
                )
            # reference elevation
            drilling_elevation = well.drilling.reference_elevation \
                if well.drilling.reference_elevation else ReferenceElevation()
            drilling_elevation_form = self.make_form(
                drilling_elevation, ReferenceElevationForm, data['drilling']['reference_elevation'])

            water_strikes = []
            for water_strike in data['drilling']['water_strike']:
                obj = WaterStrike.objects.get(
                    id=water_strike['id_']) if water_strike['id_'] else WaterStrike()

                water_strikes.append(
                    self.make_form(
                        obj, WaterStrikeForm, water_strike
                    )
                )
            # -----------------------------------------
            # construction
            # -----------------------------------------
            construction = well.construction \
                if well.construction else Construction()
            construction_form = self.make_form(
                construction, ConstructionForm, data['construction'])

            # reference elevation
            construction_elevation = well.construction.reference_elevation \
                if well.construction.reference_elevation else ReferenceElevation()
            construction_elevation_form = self.make_form(
                construction_elevation, ReferenceElevationForm, data['construction']['reference_elevation'])

            casings = []
            for casing in data['construction']['casing']:
                obj = Casing.objects.get(
                    id=casing['id_']) if casing['id_'] else Casing()

                casings.append(
                    self.make_form(
                        obj, CasingForm, casing
                    )
                )
            screens = []
            for screen in data['construction']['screen']:
                obj = Screen.objects.get(
                    id=screen['id_']) if screen['id_'] else Screen()

                screens.append(
                    self.make_form(
                        obj, ScreenForm, screen
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
            # save all forms
            # -----------------------------------------
            drilling_elevation_form.save()
            drilling_form.instance.reference_elevation = drilling_elevation_form.instance
            drilling_form.save()
            for water_strike in water_strikes:
                water_strike.instance.drilling = drilling_form.instance
                water_strike.save()
            for log in stratigraphic_log:
                log.instance.drilling = drilling_form.instance
                log.save()

            construction_elevation_form.save()
            construction_form.instance.reference_elevation = construction_elevation_form.instance
            construction_form.save()
            for casing in casings:
                casing.instance.construction = construction_form.instance
                casing.save()
            for screen in screens:
                screen.instance.construction = construction_form.instance
                screen.save()

            pumping_test_form.save()
            hydrogeo.pumping_test = pumping_test_form.instance
            hydrogeo_form.save()

            license_form.save()
            management.license = license_form.instance
            management_form.save()

            well.drilling = drilling_form.instance
            well.construction = construction_form.instance
            well.hydrogeology_parameter = hydrogeo_form.instance
            well.management = management
            general_information.save()

            for document in documents:
                document.save()
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse('OK')
