from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.models.general import Country


class CountryAutocompleteAPI(APIView):
    permission_classes = []
    """Return country list."""

    def get(self, request, *args):
        return Response([
            {
                'id': country.id,
                'label': country.name
            } for country in Country.objects.filter(
                name__icontains=request.GET.get('q', '-'))
        ])
