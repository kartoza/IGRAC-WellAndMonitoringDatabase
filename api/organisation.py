from rest_framework.views import APIView
from rest_framework.response import Response
from gwml2.models.well_management.organisation import Organisation


class OrganisationAutocompleteAPI(APIView):
    permission_classes = []
    """
    Return status of the upload session
    """

    def get(self, request, *args):
        return Response([
            {
                'id': org.id,
                'label': org.name
            } for org in Organisation.objects.filter(name__icontains=request.GET.get('q', '-'))
        ])
