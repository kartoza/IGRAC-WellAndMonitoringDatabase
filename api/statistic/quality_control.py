from django.db.models import Count, Q
from rest_framework.response import Response

from .base import BaseStatisticAPI
from gwml2.models.well import Well

class QualityControlStatisticAPI(BaseStatisticAPI):
    """Return statistic of all active organisations."""

    permission_classes = []

    def post(self, request, *args):
        ggmn_ids = self.ggmn_organisation_ids

        data_type = request.data.get('data_type')
        if data_type == 'GGMN':
            organisation_ids = self.ggmn_organisation_ids
        elif data_type == 'Groundwater Observations Repository':
            organisation_ids = self.organisations.exclude(
                id__in=ggmn_ids
            ).values_list('id', flat=True)
        else:
            organisation_ids = self.organisations.values_list('id', flat=True)

        country_ids = request.data.get('country_ids', None)
        wells = Well.objects.filter(
            organisation_id__in=organisation_ids
        )
        if country_ids:
            wells = wells.filter(country_id__in=country_ids)

        stats = wells.aggregate(
            total=Count('id', distinct=True),
            with_quality=Count('wellqualitycontrol'),
            groundwater_level_time_gap_num=Count(
                'wellqualitycontrol',
                filter=Q(
                    wellqualitycontrol__groundwater_level_time_gap__isnull=(
                        False
                    )
                ),
            ),
            groundwater_level_value_gap_num=Count(
                'wellqualitycontrol',
                filter=Q(
                    wellqualitycontrol__groundwater_level_value_gap__isnull=(
                        False
                    )
                ),
            ),
            groundwater_level_strange_value_num=Count(
                'wellqualitycontrol',
                filter=Q(
                    wellqualitycontrol__groundwater_level_strange_value__isnull=(  # noqa: E501
                        False
                    )
                ),
            ),
            quality_no_flag=Count(
                'wellqualitycontrol',
                filter=Q(
                    wellqualitycontrol__groundwater_level_time_gap__isnull=(
                        True
                    ),
                    wellqualitycontrol__groundwater_level_value_gap__isnull=(
                        True
                    ),
                    wellqualitycontrol__groundwater_level_strange_value__isnull=(  # noqa: E501
                        True
                    ),
                ),
            ),
        )
        correct_count = stats['total'] - stats['with_quality']
        no_flag = stats['quality_no_flag'] + correct_count

        return Response({
            'groundwater_level_time_gap_num': (
                stats['groundwater_level_time_gap_num']
            ),
            'groundwater_level_value_gap_num': (
                stats['groundwater_level_value_gap_num']
            ),
            'groundwater_level_strange_value_num': (
                stats['groundwater_level_strange_value_num']
            ),
            'no_flag': no_flag,
        })
