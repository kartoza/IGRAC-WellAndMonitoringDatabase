"""Test for Organisation and Country Statistic API."""
import datetime

from django.test import Client
from django.urls import reverse

from gwml2.models.general import Country
from gwml2.models.well_management.organisation import OrganisationGroup
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF


class OrganisationStatisticAPITest(GWML2Test):
    """Test for the Organisation Statistic API."""

    def setUp(self):
        """To setup test."""
        self.url = reverse('organisation_statistic')
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
        self.assertIsNone(data['country_name'])

    def test_returns_country_name_when_organisation_has_country(self):
        """country_name reflects the organisation's related country."""
        country = Country.objects.create(name='Indonesia', code='ID')
        organisation = OrganisationF(
            name='Organisation with country', country=country
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data['organisations'][0]
        self.assertEqual(data['id'], organisation.id)
        self.assertEqual(data['country_name'], 'Indonesia')

    def test_country_name_is_none_when_organisation_has_no_country(self):
        """Organisation without a country does not error and reports
        country_name as None."""
        OrganisationF(name='Organisation without country', country=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data['organisations'][0]
        self.assertIsNone(data['country_name'])

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
        flagged via is_ggmn, since this endpoint returns all active
        organisations regardless of GGMN membership."""
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


class CountryStatisticAPITest(GWML2Test):
    """Test for the Country Statistic API."""

    def setUp(self):
        """To setup test."""
        self.url = reverse('countries_statistic')
        self.client = Client()

    def test_empty(self):
        """No country returns count 0 and empty list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['countries'], [])

    def test_returns_country_with_repository_metadata_cache(self):
        """Country with an active organisation and a populated
        Observations Repository metadata cache is returned with both
        cache values."""
        country = Country.objects.create(
            name='Country 1', code='C1',
            metadata_cache_observations_repository={'count_well': 2},
            metadata_cache_ggmn={'count_well': 1},
        )
        OrganisationF(name='Organisation 1', country=country)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        data = response.data['countries'][0]
        self.assertEqual(data['id'], country.id)
        self.assertEqual(data['name'], 'Country 1')
        self.assertEqual(
            data['statistic_observations_repository'], {'count_well': 2}
        )
        self.assertEqual(data['statistic_ggmn'], {'count_well': 1})

    def test_excludes_country_without_organisation(self):
        """Country with no organisation is not included."""
        Country.objects.create(
            name='Country without org', code='C0',
            metadata_cache_observations_repository={'count_well': 3},
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_excludes_country_with_zero_well_counts(self):
        """Country whose caches both have count_well 0 is not
        included."""
        country = Country.objects.create(
            name='Country zero', code='C2',
            metadata_cache_observations_repository={'count_well': 0},
            metadata_cache_ggmn={'count_well': 0},
        )
        OrganisationF(name='Organisation zero', country=country)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_excludes_country_with_null_metadata_cache(self):
        """Country whose metadata caches were never generated is not
        included."""
        country = Country.objects.create(name='Country null', code='C3')
        OrganisationF(name='Organisation null', country=country)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_includes_country_with_only_ggmn_well_count(self):
        """A country whose Observations Repository cache has no wells
        is still included if its GGMN-specific cache does."""
        country = Country.objects.create(
            name='Country ggmn only', code='C4',
            metadata_cache_observations_repository={'count_well': 0},
            metadata_cache_ggmn={'count_well': 3},
        )
        OrganisationF(name='Organisation ggmn only', country=country)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        data = response.data['countries'][0]
        self.assertEqual(data['name'], 'Country ggmn only')
        self.assertEqual(data['statistic_ggmn'], {'count_well': 3})

    def test_includes_country_with_only_repository_well_count(self):
        """A country whose GGMN cache has no wells (or was never
        generated) is still included if its Observations Repository
        cache does."""
        country = Country.objects.create(
            name='Country repository only', code='C5',
            metadata_cache_observations_repository={'count_well': 4},
        )
        OrganisationF(name='Organisation repository only', country=country)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        data = response.data['countries'][0]
        self.assertEqual(data['name'], 'Country repository only')
        self.assertEqual(
            data['statistic_observations_repository'], {'count_well': 4}
        )

    def test_includes_country_with_ggmn_organisation(self):
        """A country is included regardless of whether its organisation
        belongs to the GGMN group, since this endpoint covers every
        active organisation."""
        ggmn_group = OrganisationGroup.objects.create(name='GGMN')
        ggmn_country = Country.objects.create(
            name='GGMN country', code='G1',
            metadata_cache_ggmn={'count_well': 2},
        )
        ggmn_organisation = OrganisationF(
            name='GGMN organisation', country=ggmn_country
        )
        ggmn_group.organisations.add(ggmn_organisation)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['countries'][0]['name'], 'GGMN country'
        )