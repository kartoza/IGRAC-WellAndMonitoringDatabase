from rest_framework.views import APIView

from gwml2.models.well_management.organisation import (
    Organisation, OrganisationGroup
)


class BaseStatisticAPI(APIView):
    """Base for statistic APIs."""

    permission_classes = []
    is_ggmn = False

    @property
    def ggmn_organisation_ids(self):
        """Return GGMN group."""
        # GGMN Group
        ggmn_group = OrganisationGroup.get_ggmn_group()
        return set(
            ggmn_group.organisations.values_list('id', flat=True)
        ) if ggmn_group else set()

    @property
    def organisations(self):
        """Return queryset of organizations."""
        if self.is_ggmn:
            ggmn_group = OrganisationGroup.get_ggmn_group()
            if not ggmn_group:
                return Organisation.objects.none()
            return ggmn_group.organisations.filter(active=True)
        else:
            return Organisation.objects.filter(active=True)
