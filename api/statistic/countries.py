from rest_framework.response import Response

from gwml2.models.general import Country
from .base import BaseStatisticAPI


class BaseCountryStatisticAPI(BaseStatisticAPI):
    """Base for country statistic APIs."""

    permission_classes = []

    def get(self, request, *args):
        organisations = self.organisations
        cache_field = (
            'metadata_cache_ggmn' if self.is_ggmn else 'metadata_cache'
        )
        query = Country.objects.filter(
            **{
                f'{cache_field}__isnull': False,
                f'{cache_field}__count_well__gt': 0,
            },
            id__in=organisations.values_list('country_id', flat=True)
        )

        countries = []
        for obj in query:
            countries.append({
                'id': obj.id,
                'name': obj.name,
                'statistic': obj.metadata_cache,
                'statistic_ggmn': obj.metadata_cache_ggmn,
            })
        return Response({
            'count': len(countries),
            'countries': countries,
        })


class CountryStatisticAPI(BaseCountryStatisticAPI):
    """Return statistic of all country."""

    is_ggmn = False


class CountryGGMNStatisticAPI(BaseCountryStatisticAPI):
    """Return statistic of GGMN country."""

    is_ggmn = True
