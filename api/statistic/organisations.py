from rest_framework.response import Response

from .base import BaseStatisticAPI


class OrganisationStatisticAPI(BaseStatisticAPI):
    """Return statistic of all active organisations."""

    permission_classes = []

    def get(self, request, *args):
        query = self.organisations.select_related('country')

        ggmn_ids = self.ggmn_organisation_ids

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
                'country_name': obj.country.name if obj.country else None,
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
