import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import View
from gwml2.mixin import ViewWellFormMixin, EditWellFormMixin
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well
from gwml2.views.form_group.general_information import (
    GeneralInformationGetForms, GeneralInformationCreateForm
)
from gwml2.views.form_group.geology import (
    GeologyGetForms, GeologyCreateForm
)
from gwml2.views.form_group.construction import (
    ConstructionGetForms, ConstructionCreateForm
)
from gwml2.views.form_group.drilling import (
    DrillingGetForms, DrillingCreateForm
)
from gwml2.views.form_group.hydrogeology import (
    HydrogeologyGetForms, HydrogeologyCreateForm
)
from gwml2.views.form_group.management import (
    ManagementGetForms, ManagementCreateForm
)
from gwml2.views.form_group.yield_measurement import (
    YieldMeasurementGetForms, YieldMeasurementCreateForm
)
from gwml2.views.form_group.quality_measurement import (
    QualityMeasurementGetForms, QualityMeasurementCreateForm
)

from gwml2.views.form_group.level_measurement import (
    LevelMeasurementGetForms, LevelMeasurementCreateForm
)


class FormNotValid(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class WellView(ViewWellFormMixin, View):
    read_only = True

    def get_context(self, well):
        context = {
            'read_only': self.read_only,
            'is_admin': well.organisation.is_admin(self.request.user) if well.organisation else False,
            'well': well,
            'parameters': {
                measurement.id: [unit.name for unit in measurement.units.all()] for measurement in TermMeasurementParameter.objects.all()
            }
        }
        context.update(GeneralInformationGetForms(well).get())
        context.update(GeologyGetForms(well).get())
        context.update(DrillingGetForms(well).get())
        context.update(ConstructionGetForms(well).get())
        context.update(HydrogeologyGetForms(well).get())
        context.update(ManagementGetForms(well).get_form(self.request.user))
        context.update(YieldMeasurementGetForms(well).get())
        context.update(QualityMeasurementGetForms(well).get())
        context.update(LevelMeasurementGetForms(well).get())
        return context

    def get(self, request, id, *args, **kwargs):
        well = get_object_or_404(Well, id=id)

        context = self.get_context(well)
        return render(
            request, 'groundwater_form/main.html',
            context
        )


class WellFormView(EditWellFormMixin, WellView):
    read_only = False

    def make_form(self, instance, form, data):
        """ make form from data

        :rtype: ModelForm
        """
        form = form.make_from_data(
            instance, data, self.request.FILES)
        if not form.is_valid():
            raise FormNotValid(json.dumps(form.errors))
        return form

    def create_data(self, well, data):
        general_information = GeneralInformationCreateForm(well, data, self.request.FILES)
        geology = GeologyCreateForm(well, data, self.request.FILES)
        drilling = DrillingCreateForm(well, data, self.request.FILES)
        construction = ConstructionCreateForm(well, data, self.request.FILES)
        hydrogeology = HydrogeologyCreateForm(well, data, self.request.FILES)
        management = ManagementCreateForm(well, data, self.request.FILES)
        yield_measurement = YieldMeasurementCreateForm(well, data, self.request.FILES)
        quality_measurement = QualityMeasurementCreateForm(well, data, self.request.FILES)
        level_measurement = LevelMeasurementCreateForm(well, data, self.request.FILES)

        # -----------------------------------------
        # save all forms
        # -----------------------------------------
        geology.save()
        construction.save()
        drilling.save()
        management.save()
        hydrogeology.save()
        yield_measurement.save()
        quality_measurement.save()
        level_measurement.save()
        general_information.save()

    def post(self, request, id, *args, **kwargs):
        data = json.loads(request.POST['data'])
        well = get_object_or_404(Well, id=id)

        try:
            self.create_data(well, data)
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse(reverse('well_form', kwargs={'id': well.id}))


class WellFormCreateView(WellFormView):
    read_only = False

    def get(self, request, *args, **kwargs):
        well = Well()

        context = self.get_context(well)
        return render(
            request, 'groundwater_form/main.html',
            context
        )

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST['data'])
        general_information = GeneralInformationCreateForm(Well(), data, self.request.FILES)
        general_information.save()
        well = general_information.form.instance

        try:
            self.create_data(well, data)
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse(reverse('well_form', kwargs={'id': well.id}))
