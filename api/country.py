from django.conf import settings
from django.db import connections
from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.models.general import Country
from gwml2.models.well_management.organisation import OrganisationGroup


class CountryAutocompleteAPI(APIView):
    """Return country list."""

    permission_classes = []

    def get(self, request, *args):
        query = Country.objects.all()

        # Query by data type
        data_type = request.GET.get('data_type', None)
        if data_type:
            if data_type.lower() == 'ggmn':
                ggmn_group = OrganisationGroup.get_ggmn_group()
                if not ggmn_group:
                    query = query.none()
                else:
                    query = Country.objects.filter(
                        id__in=ggmn_group.organisations.all().values_list(
                            'country_id', flat=True
                        )
                    )
            elif data_type.lower() == 'well and monitoring data':
                with connections[
                    settings.GWML2_DATABASE_CONFIG].cursor() as cursor:
                    cursor.execute(
                        "SELECT DISTINCT country_id FROM well WHERE country_id IS NOT NULL;")
                    query = Country.objects.filter(
                        id__in=[row[0] for row in cursor.fetchall()]
                    )
            else:
                query = query.none()

        q = request.GET.get('q', None)
        if q:
            query = query.filter(name__icontains=q)

        # Return data
        return Response([
            {
                'id': obj.id,
                'label': obj.name
            } for obj in query
        ])
