from django.shortcuts import render
from rest_framework.views import APIView

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

        # Render the contributor page template with organisations
        return render(
            request,
            'groundwater/well_dashboard.html',
            {
                'data_type': data_type,
                'title': TITLES.get(data_type, 'Stations Dashboard'),
            }
        )