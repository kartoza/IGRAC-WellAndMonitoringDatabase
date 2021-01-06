import json
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import View
from gwml2.mixin import ViewWellFormMixin, EditWellFormMixin
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.reference_elevation import TermReferenceElevationType
from gwml2.models.well import Well
from gwml2.views.form_group.form_group import FormNotValid
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
from gwml2.views.form_group.well_metadata import (
    WellMetadataGetForms, WellMetadataCreateForm
)


class WellView(ViewWellFormMixin, View):
    read_only = True

    def get_context(self, well):
        context = {
            'read_only': self.read_only,
            'well': well,
            'parameters': {
                measurement.id: [unit.name for unit in measurement.units.all()] for measurement in TermMeasurementParameter.objects.all()
            },
            'reference_elevations': {
                type.id: type.name for type in TermReferenceElevationType.objects.all()
            }
        }
        if well.pk and not well.ggis_uid:
            well.save()

        context.update(GeneralInformationGetForms(well).get())
        context.update(GeologyGetForms(well).get())
        context.update(DrillingGetForms(well).get())
        context.update(ConstructionGetForms(well).get())
        context.update(HydrogeologyGetForms(well).get())
        context.update(ManagementGetForms(well).get())
        context.update(YieldMeasurementGetForms(well).get())
        context.update(QualityMeasurementGetForms(well).get())
        context.update(LevelMeasurementGetForms(well).get())
        context.update(WellMetadataGetForms(well).get_form(self.request.user))
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
    general_information = None
    geology = None
    drilling = None
    construction = None
    hydrogeology = None
    management = None
    yield_measurement = None
    quality_measurement = None
    level_measurement = None
    well_metadata = None

    @transaction.atomic
    def edit_well(self, well, data, FILES, user):
        """ Edit well with data and FILES

        :param well: well that will be edited
        :type well: Well

        :param data: data that will be inserted
        :type data: dict

        :param FILES: files to be inserted
        :type FILES: dict

        :param user: user that edit the well
        :type user: User
        """

        # create new well if well is not provided
        if not well:
            general_information = GeneralInformationCreateForm(Well(), data, FILES)
            general_information.save()
            well = general_information.form.instance

        self.general_information = GeneralInformationCreateForm(well, data, FILES)
        self.geology = GeologyCreateForm(well, data, FILES)
        self.drilling = DrillingCreateForm(well, data, FILES)
        self.construction = ConstructionCreateForm(well, data, FILES)
        self.hydrogeology = HydrogeologyCreateForm(well, data, FILES)
        self.management = ManagementCreateForm(well, data, FILES)
        self.yield_measurement = YieldMeasurementCreateForm(well, data, FILES)
        self.quality_measurement = QualityMeasurementCreateForm(well, data, FILES)
        self.level_measurement = LevelMeasurementCreateForm(well, data, FILES)

        if not well.created_by:
            well.created_by = user.id
        well.last_edited_by = user.id
        well.save()

        self.well_metadata = WellMetadataCreateForm(well, data, FILES)

        # -----------------------------------------
        # save all forms
        # -----------------------------------------
        self.geology.save()
        self.construction.save()
        self.drilling.save()
        self.management.save()
        self.hydrogeology.save()
        self.yield_measurement.save()
        self.quality_measurement.save()
        self.level_measurement.save()
        self.general_information.save()
        self.well_metadata.save()

        return well


class WellFormView(WellEditing, EditWellFormMixin, WellView):
    read_only = False

    def post(self, request, id, *args, **kwargs):
        data = json.loads(request.POST['data'])
        well = get_object_or_404(Well, id=id)

        self.edit_well(well, data, self.request.FILES, request.user)

        return HttpResponse(reverse('well_view', kwargs={'id': well.id}))


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
            well = self.edit_well(None, data, self.request.FILES, request.user)
        except KeyError as e:
            return HttpResponseBadRequest('{} is needed'.format(e))
        except (ValueError, FormNotValid, Exception) as e:
            return HttpResponseBadRequest('{}'.format(e))

        return HttpResponse(reverse('well_view', kwargs={'id': well.id}))
