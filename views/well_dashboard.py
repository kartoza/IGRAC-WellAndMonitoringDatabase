from django.shortcuts import render
from rest_framework.views import APIView


class WellDashboardView(APIView):
    """Well dashboard view."""

    def get(self, request):
        # Render the contributor page template with organisations
        return render(
            request,
            'groundwater/well_dashboard.html'

        )
