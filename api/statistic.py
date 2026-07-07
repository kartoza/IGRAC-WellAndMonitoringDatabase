from rest_framework.response import Response
from rest_framework.views import APIView

from gwml2.models.well_management.organisation import (
    Organisation, OrganisationGroup
)


class BaseOrganisationStatisticAPI(APIView):
    """Base for organisation statistic APIs."""

    permission_classes = []

    def get_queryset(self):
        """Return queryset of active organisations for this statistic."""
        raise NotImplementedError

    def get(self, request, *args):
        query = self.get_queryset()
        ggmn_group = OrganisationGroup.get_ggmn_group()
        ggmn_ids = set(
            ggmn_group.organisations.values_list('id', flat=True)
        ) if ggmn_group else set()
        count_well = 0
        count_spring = 0
        count_well_with_level = 0
        count_well_with_quality = 0
        organisations = []
        for obj in query:
            stats = obj.data_stats or {}
            count_well += stats.get('count_well', 0) or 0
            count_spring += stats.get('count_spring', 0) or 0
            count_well_with_level += (
                stats.get('count_well_with_level', 0) or 0
            )
            count_well_with_quality += (
                stats.get('count_well_with_quality', 0) or 0
            )
            organisations.append({
                'id': obj.id,
                'name': obj.name,
                'is_ggmn': obj.id in ggmn_ids,
                'data_is_from_api': obj.data_is_from_api,
                'data_date_start': obj.data_date_start,
                'data_date_end': obj.data_date_end,
                'data_stats': obj.data_stats,
                'metadata_cache_generated_at': (
                    obj.metadata_cache_generated_at
                ),
            })
        return Response({
            'count': len(organisations),
            'count_well': count_well,
            'count_spring': count_spring,
            'count_well_with_level': count_well_with_level,
            'count_well_with_quality': count_well_with_quality,
            'organisations': organisations,
        })


class OrganisationStatisticAPI(BaseOrganisationStatisticAPI):
    """Return statistic of all active organisations."""

    def get_queryset(self):
        return Organisation.objects.filter(active=True)


class OrganisationGGMNStatisticAPI(BaseOrganisationStatisticAPI):
    """Return statistic of GGMN organisations."""

    def get_queryset(self):
        ggmn_group = OrganisationGroup.get_ggmn_group()
        if not ggmn_group:
            return Organisation.objects.none()
        return ggmn_group.organisations.filter(active=True)