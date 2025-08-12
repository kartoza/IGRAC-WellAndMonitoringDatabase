from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.models.well_management.organisation import (
    Organisation, OrganisationGroup
)


class OrganisationAutocompleteAPI(APIView):
    """Return status of the upload session."""

    permission_classes = []

    def get(self, request, *args):
        query = Organisation.objects.all()

        # Query by data type
        data_type = request.GET.get('data_type', None)
        if data_type:
            ggmn_group = OrganisationGroup.get_ggmn_group()
            if data_type.lower() == 'ggmn':
                if not ggmn_group:
                    query = query.none()
                else:
                    query = ggmn_group.organisations.all()
            elif data_type.lower() == 'well and monitoring data':
                if ggmn_group:
                    query = Organisation.objects.exclude(
                        id__in=ggmn_group.organisations.values_list(
                            'id', flat=True
                        )
                    )
            else:
                query = query.none()

        # Return data
        query = query.filter(active=True)
        return Response([
            {
                'id': obj.id,
                'label': obj.name
            } for obj in query
        ])
