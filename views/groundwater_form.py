import json
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from braces.views import StaffuserRequiredMixin
from django.views.generic.base import View
from gwml2.models.well import Well
from gwml2.views.form_group.general_information import (
    GeneralInformationGetForms, GeneralInformationCreateForm
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


class WellFormView(StaffuserRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        well = get_object_or_404(Well, id=id)

        context = {}
        context.update(GeneralInformationGetForms(well).get())
        context.update(DrillingGetForms(well).get())
        context.update(ConstructionGetForms(well).get())
        context.update(HydrogeologyGetForms(well).get())
        context.update(ManagementGetForms(well).get())
        context.update(YieldMeasurementGetForms(well).get())
        context.update(QualityMeasurementGetForms(well).get())
        context.update(LevelMeasurementGetForms(well).get())
        return render(
            request, 'groundwater_form/main.html',
            context
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
            general_information = GeneralInformationCreateForm(well, data, self.request.FILES)
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
            construction.save()
            drilling.save()
            management.save()
            hydrogeology.save()
            yield_measurement.save()
            quality_measurement.save()
            level_measurement.save()
            general_information.save()
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse('OK')
