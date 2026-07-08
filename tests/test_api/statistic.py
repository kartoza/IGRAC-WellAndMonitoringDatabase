"""Test for Organisation and Country Statistic API."""
import datetime
import json

from django.test import Client
from django.urls import reverse

from gwml2.models.general import Country
from gwml2.models.well_management.organisation import OrganisationGroup
from gwml2.models.well_quality_control import WellQualityControl
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF, WellF


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
        self.assertIsNone(data['country_id'])

    def test_returns_country_id_when_organisation_has_country(self):
        """country_id reflects the organisation's related country."""
        country = Country.objects.create(name='Indonesia', code='ID')
        organisation = OrganisationF(
            name='Organisation with country', country=country
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data['organisations'][0]
        self.assertEqual(data['id'], organisation.id)
        self.assertEqual(data['country_id'], country.id)

    def test_country_id_is_none_when_organisation_has_no_country(self):
        """Organisation without a country does not error and reports
        country_id as None."""
        OrganisationF(name='Organisation without country', country=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.data['organisations'][0]
        self.assertIsNone(data['country_id'])

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
        ggmn_group = OrganisationGroup.get_ggmn_group()
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
        ggmn_group = OrganisationGroup.get_ggmn_group()
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


class QualityControlStatisticAPITest(GWML2Test):
    """Test for the Quality Control Statistic API."""

    def setUp(self):
        """To setup test."""
        self.url = reverse('quality_control_statistic')
        self.client = Client()

    def post(self, data=None):
        """Post data as JSON, as country_ids is a list."""
        return self.client.post(
            self.url,
            data=json.dumps(data or {}),
            content_type='application/json',
        )

    def test_empty(self):
        """No well returns all counts as 0."""
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['groundwater_level_time_gap_num'], 0)
        self.assertEqual(response.data['groundwater_level_value_gap_num'], 0)
        self.assertEqual(
            response.data['groundwater_level_strange_value_num'], 0
        )
        self.assertEqual(response.data['no_flag'], 0)

    def test_well_without_any_flag_counts_as_no_flag(self):
        """A well is auto-assigned an empty WellQualityControl record on
        creation (see the post_save signal); with no flags set it should
        be counted under no_flag only."""
        WellF(name='Well 1')
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['groundwater_level_time_gap_num'], 0)
        self.assertEqual(response.data['groundwater_level_value_gap_num'], 0)
        self.assertEqual(
            response.data['groundwater_level_strange_value_num'], 0
        )
        self.assertEqual(response.data['no_flag'], 1)

    def test_well_without_quality_control_record_counts_as_no_flag(self):
        """A well whose auto-created WellQualityControl record was
        removed is still counted under no_flag via correct_count."""
        well = WellF(name='Well without quality control')
        WellQualityControl.objects.filter(well=well).delete()
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 1)

    def test_counts_well_with_time_gap_flag(self):
        """Well flagged with groundwater_level_time_gap is counted under
        groundwater_level_time_gap_num and not under no_flag."""
        well = WellF(name='Well with time gap')
        quality = WellQualityControl.objects.get(well=well)
        quality.groundwater_level_time_gap = {'flag': True}
        quality.save()
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['groundwater_level_time_gap_num'], 1)
        self.assertEqual(response.data['no_flag'], 0)

    def test_counts_well_with_value_gap_flag(self):
        """Well flagged with groundwater_level_value_gap is counted under
        groundwater_level_value_gap_num and not under no_flag."""
        well = WellF(name='Well with value gap')
        quality = WellQualityControl.objects.get(well=well)
        quality.groundwater_level_value_gap = {'flag': True}
        quality.save()
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['groundwater_level_value_gap_num'], 1)
        self.assertEqual(response.data['no_flag'], 0)

    def test_counts_well_with_strange_value_flag(self):
        """Well flagged with groundwater_level_strange_value is counted
        under groundwater_level_strange_value_num and not under
        no_flag."""
        well = WellF(name='Well with strange value')
        quality = WellQualityControl.objects.get(well=well)
        quality.groundwater_level_strange_value = {'flag': True}
        quality.save()
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['groundwater_level_strange_value_num'], 1
        )
        self.assertEqual(response.data['no_flag'], 0)

    def test_excludes_well_of_inactive_organisation(self):
        """A well under an inactive organisation is excluded entirely."""
        organisation = OrganisationF(
            name='Inactive organisation', active=False
        )
        WellF(name='Well of inactive organisation', organisation=organisation)
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 0)

    def test_filters_by_data_type_ggmn(self):
        """data_type='GGMN' only counts wells of GGMN organisations."""
        ggmn_group = OrganisationGroup.get_ggmn_group()
        ggmn_organisation = OrganisationF(name='GGMN organisation')
        ggmn_group.organisations.add(ggmn_organisation)
        regular_organisation = OrganisationF(name='Regular organisation')

        WellF(name='GGMN well', organisation=ggmn_organisation)
        WellF(name='Regular well', organisation=regular_organisation)

        response = self.post({'data_type': 'GGMN'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 1)

    def test_filters_by_data_type_observations_repository(self):
        """data_type='Groundwater Observations Repository' excludes
        wells of GGMN organisations."""
        ggmn_group = OrganisationGroup.get_ggmn_group()
        ggmn_organisation = OrganisationF(name='GGMN organisation')
        ggmn_group.organisations.add(ggmn_organisation)
        regular_organisation = OrganisationF(name='Regular organisation')

        WellF(name='GGMN well', organisation=ggmn_organisation)
        WellF(name='Regular well', organisation=regular_organisation)

        response = self.post(
            {'data_type': 'Groundwater Observations Repository'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 1)

    def test_filters_by_country_ids(self):
        """country_ids restricts the counted wells to those countries."""
        country_a = Country.objects.create(name='Country A', code='CA')
        country_b = Country.objects.create(name='Country B', code='CB')

        WellF(name='Well in country A', country=country_a)
        WellF(name='Well in country B', country=country_b)

        response = self.post({'country_ids': [country_a.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 1)

    def test_country_ids_empty_includes_all_wells(self):
        """An empty/absent country_ids does not filter by country."""
        country_a = Country.objects.create(name='Country A', code='CA')
        country_b = Country.objects.create(name='Country B', code='CB')

        WellF(name='Well in country A', country=country_a)
        WellF(name='Well in country B', country=country_b)

        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['no_flag'], 2)