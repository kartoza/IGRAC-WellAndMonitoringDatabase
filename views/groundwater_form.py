import json
from django.db import transaction
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


class WellEditing(object):
    """ Contains function to create/edit well"""

    @transaction.atomic
    def edit_well(self, well, data, FILES):
        """ Edit well with data and FILES

        :param well: well that will be edited
        :type well: Well

        :param data: data that will be inserted
        :type data: dict

        :param FILES: files to be inserted
        :type FILES: dict
        """

        # create new well if well is not provided
        if not well:
            general_information = GeneralInformationCreateForm(Well(), data, FILES)
            general_information.save()
            well = general_information.form.instance

        general_information = GeneralInformationCreateForm(well, data, FILES)
        geology = GeologyCreateForm(well, data, FILES)
        drilling = DrillingCreateForm(well, data, FILES)
        construction = ConstructionCreateForm(well, data, FILES)
        hydrogeology = HydrogeologyCreateForm(well, data, FILES)
        management = ManagementCreateForm(well, data, FILES)
        yield_measurement = YieldMeasurementCreateForm(well, data, FILES)
        quality_measurement = QualityMeasurementCreateForm(well, data, FILES)
        level_measurement = LevelMeasurementCreateForm(well, data, FILES)

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

        return well


class WellFormView(WellEditing, EditWellFormMixin, WellView):
    read_only = False

    def post(self, request, id, *args, **kwargs):
        data = json.loads(request.POST['data'])
        well = get_object_or_404(Well, id=id)

        try:
            self.edit_well(well, data, self.request.FILES)
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid, Exception) as e:
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

        try:
            well = self.edit_well(None, data, self.request.FILES)
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid, Exception) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse(reverse('well_form', kwargs={'id': well.id}))
