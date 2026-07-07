"""Test for Organisation Statistic API."""
import datetime

from django.test import Client
from django.urls import reverse

from gwml2.models.well_management.organisation import OrganisationGroup
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF


class OrganisationStatisticAPITest(GWML2Test):
    """Test for the general (non-GGMN) Organisation Statistic API."""

    def setUp(self):
        """To setup test."""
        self.url = reverse('organisation_statistic_general')
        self.client = Client()

    def test_empty(self):
        """No organisation returns count 0 and empty list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['count_well'], 0)
        self.assertEqual(response.data['count_spring'], 0)
        self.assertEqual(response.data['count_well_with_level'], 0)
        self.assertEqual(response.data['count_well_with_quality'], 0)
        self.assertEqual(response.data['organisations'], [])

    def test_returns_active_organisation_data(self):
        """Active organisation is returned with its cached metadata."""
        organisation = OrganisationF(
            name='Organisation 1',
            data_is_from_api=True,
            data_date_start=datetime.date(2020, 1, 1),
            data_date_end=datetime.date(2021, 6, 1),
            data_stats={'count_well': 1},
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['organisations']), 1)
        data = response.data['organisations'][0]
        self.assertEqual(data['id'], organisation.id)
        self.assertEqual(data['name'], 'Organisation 1')
        self.assertTrue(data['data_is_from_api'])
        self.assertEqual(
            data['data_date_start'], datetime.date(2020, 1, 1)
        )
        self.assertEqual(data['data_date_end'], datetime.date(2021, 6, 1))
        self.assertEqual(data['data_stats'], {'count_well': 1})
        self.assertIsNone(data['metadata_cache_generated_at'])
        self.assertFalse(data['is_ggmn'])

    def test_sums_data_stats_across_organisations(self):
        """count_well/count_spring/count_well_with_level/
        count_well_with_quality are summed across all active
        organisations' data_stats."""
        OrganisationF(
            name='Organisation A',
            data_stats={
                'count_well': 3,
                'count_spring': 1,
                'count_well_with_level': 2,
                'count_well_with_quality': 1,
            },
        )
        OrganisationF(
            name='Organisation B',
            data_stats={
                'count_well': 5,
                'count_spring': 2,
                'count_well_with_level': 1,
                'count_well_with_quality': 4,
            },
        )
        OrganisationF(name='Organisation C', data_stats=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['count_well'], 8)
        self.assertEqual(response.data['count_spring'], 3)
        self.assertEqual(response.data['count_well_with_level'], 3)
        self.assertEqual(response.data['count_well_with_quality'], 5)

    def test_excludes_inactive_organisation(self):
        """Inactive organisation is not included in the statistic."""
        OrganisationF(name='Inactive organisation', active=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['organisations'], [])

    def test_includes_ggmn_organisation(self):
        """Organisation belonging to the GGMN group is still included,
        since this endpoint returns all active organisations."""
        ggmn_group = OrganisationGroup.objects.create(name='GGMN')
        ggmn_organisation = OrganisationF(name='GGMN organisation')
        ggmn_group.organisations.add(ggmn_organisation)
        OrganisationF(name='Regular organisation')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        is_ggmn_by_name = {
            org['name']: org['is_ggmn']
            for org in response.data['organisations']
        }
        self.assertEqual(
            is_ggmn_by_name,
            {'GGMN organisation': True, 'Regular organisation': False}
        )


class OrganisationGGMNStatisticAPITest(GWML2Test):
    """Test for the GGMN Organisation Statistic API."""

    def setUp(self):
        """To setup test."""
        self.url = reverse('organisation_statistic_ggmn')
        self.client = Client()

    def test_empty_when_no_ggmn_group(self):
        """No GGMN group returns count 0 and empty list."""
        OrganisationF(name='Regular organisation')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['organisations'], [])

    def test_returns_only_ggmn_organisations(self):
        """Only organisations belonging to the GGMN group are
        returned."""
        ggmn_group = OrganisationGroup.objects.create(name='GGMN')
        ggmn_organisation = OrganisationF(
            name='GGMN organisation',
            data_stats={'count_well': 2},
        )
        ggmn_group.organisations.add(ggmn_organisation)
        OrganisationF(name='Regular organisation')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['count_well'], 2)
        self.assertEqual(
            response.data['organisations'][0]['name'], 'GGMN organisation'
        )
        self.assertTrue(response.data['organisations'][0]['is_ggmn'])

    def test_excludes_inactive_ggmn_organisation(self):
        """Inactive organisation is not included even if in the GGMN
        group."""
        ggmn_group = OrganisationGroup.objects.create(name='GGMN')
        ggmn_organisation = OrganisationF(
            name='GGMN organisation', active=False
        )
        ggmn_group.organisations.add(ggmn_organisation)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['organisations'], [])