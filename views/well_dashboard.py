from django.shortcuts import render
from rest_framework.views import APIView

from igrac.models.site_preference import SitePreference

GGMN = 'ggmn'
OBSERVATIONS_REPOSITORY = 'observations_repository'

TITLES = {
    GGMN: 'GGMN Stations Dashboard',
    OBSERVATIONS_REPOSITORY: (
        'Groundwater Observations Repository Stations Dashboard'
    ),
}


class WellDashboardView(APIView):
    """Well dashboard view."""

    def get(self, request):
        data_type = request.GET.get('data-type')
        if data_type not in (GGMN, OBSERVATIONS_REPOSITORY):
            data_type = None

        resource_body = None
        if data_type:
            pref = SitePreference.objects.first()
            if data_type == GGMN and pref.dashboard_ggmn_popup:
                resource_body = '<hr/>'.join(
                    [pref.dashboard_ggmn_popup.body]
                )
            elif (
                    data_type == OBSERVATIONS_REPOSITORY and pref.dashboard_repository_popup
            ):
                resource_body = '<hr/>'.join(
                    [pref.dashboard_repository_popup.body]
                )

        # Render the contributor page template with organisations
        return render(
            request,
            'groundwater/well_dashboard.html',
            {
                'data_type': data_type,
                'title': TITLES.get(data_type, 'Stations Dashboard'),
                'resource_body': resource_body,
            }
        )
