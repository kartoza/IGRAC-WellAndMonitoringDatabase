from django.db.models import Q
from rest_framework.response import Response

from gwml2.models.general import Country
from .base import BaseStatisticAPI


class CountryStatisticAPI(BaseStatisticAPI):
    """Return statistic of all countries."""

    permission_classes = []

    def get(self, request, *args):
        organisations = self.organisations
        cache_filter = (
            Q(
                metadata_cache_observations_repository__isnull=False,
                metadata_cache_observations_repository__count_well__gt=0,
            ) |
            Q(
                metadata_cache_ggmn__isnull=False,
                metadata_cache_ggmn__count_well__gt=0,
            )
        )
        query = Country.objects.filter(
            cache_filter,
            id__in=organisations.values_list('country_id', flat=True)
        )

        countries = []
        for obj in query:
            countries.append({
                'id': obj.id,
                'name': obj.name,
                'statistic_observations_repository': (
                    obj.metadata_cache_observations_repository
                ),
                'statistic_ggmn': obj.metadata_cache_ggmn,
            })
        return Response({
            'count': len(countries),
            'countries': countries,
        })
