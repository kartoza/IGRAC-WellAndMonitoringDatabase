""" Delete wells in background.

Just show the wells just the count of data
"""
import json

from django.contrib.admin import helpers
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import (
    render, get_object_or_404
)
from django.utils.translation import gettext as _
from django.views.generic.list import View

from gwml2.admin.well import WellAdmin
from gwml2.models.well import (
    Well,
    WellLevelMeasurement, WellYieldMeasurement, WellQualityMeasurement
)
from gwml2.models.well_deletion import WellDeletion


def delete_well_in_background(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied()

    opts = modeladmin.model._meta
    well_count = queryset.count()
    ids = queryset.values_list('id', flat=True)
    well_level_count = WellLevelMeasurement.objects.filter(
        well_id__in=ids
    ).count()
    well_yield_count = WellYieldMeasurement.objects.filter(
        well_id__in=ids
    ).count()
    well_quality_count = WellQualityMeasurement.objects.filter(
        well_id__in=ids
    ).count()
    organisations = queryset.values('organisation__name').annotate(
        count=Count('id')
    ).order_by('organisation')

    title = _("Are you sure?")
    data = {
        'organisations': list(organisations),
        'count': {
            'well': int(well_count),
            'level': int(well_level_count),
            'yield': int(well_yield_count),
            'quality': int(well_quality_count),
        },
    }
    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
        'data': data,
        'ids': list(ids),
        'data_in_json': json.dumps(data)
    }

    request.current_app = modeladmin.admin_site.name

    return render(
        request,
        'admin/delete_selected_confirmation_background.html',
        context
    )


class DeleteWellPostView(View):
    """Delete on in view."""

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()
        data = request.POST.copy()
        detail = json.loads(data['data'])
        ids = json.loads(data['ids'])
        WellDeletion.objects.create(
            user=request.user.id,
            data=detail,
            ids=ids
        )
        return render(
            request, 'admin/delete_selected_confirmation_background.html',
            {}
        )


class DeleteWellProgressView(View):
    """Delete on in view."""

    def get(self, request, uuid, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()

        progress = get_object_or_404(WellDeletion, identifier=uuid)
        modeladmin = WellAdmin(Well, AdminSite())
        opts = modeladmin.model._meta
        context = {
            **modeladmin.admin_site.each_context(request),
            'title': 'Deleting progress.',
            'opts': opts,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'media': modeladmin.media,
            'data': progress.data,
            'isProgress': True
        }

        request.current_app = modeladmin.admin_site.name

        return render(
            request,
            'admin/delete_selected_confirmation_background.html',
            context
        )


class DeleteWellProgressData(View):
    """Delete on in view."""

    def get(self, request, uuid, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()

        progress = get_object_or_404(WellDeletion, identifier=uuid)
        return HttpResponse(progress.progress)
