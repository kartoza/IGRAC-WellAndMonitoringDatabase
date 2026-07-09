"""Test for OrganisationContributorSerializer."""

import datetime

from gwml2.models.well_management.organisation import OrganisationLink
from gwml2.serializer.organisation_contributor import (
    OrganisationContributorSerializer
)
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import OrganisationF


class OrganisationContributorSerializerTest(GWML2Test):
    """Test for OrganisationContributorSerializer."""

    def setUp(self):
        """To setup test."""
        self.organisation = OrganisationF(
            name='Organisation 1', description='Description 1'
        )

    def serialize(self):
        """Return serialized data for self.organisation."""
        return OrganisationContributorSerializer(self.organisation).data

    def test_defaults_when_no_data(self):
        """All counts default to 0 and data_types is empty when there
        is no stats data."""
        data = self.serialize()
        self.assertEqual(data['name'], 'Organisation 1')
        self.assertEqual(data['description'], 'Description 1')
        self.assertEqual(data['links'], [])
        self.assertEqual(data['data_types'], '')
        self.assertEqual(data['time_range'], '')
        self.assertEqual(data['count_stations'], 0)
        self.assertEqual(data['count_stations_level'], 0)
        self.assertEqual(data['count_stations_quality'], 0)
        self.assertEqual(data['count_springs'], 0)

    def test_links(self):
        """Links are serialized as name/url dicts."""
        OrganisationLink.objects.create(
            organisation=self.organisation,
            name='Website',
            url='https://example.com'
        )
        data = self.serialize()
        self.assertEqual(
            data['links'], [{'name': 'Website', 'url': 'https://example.com'}]
        )

    def test_data_types_joins_level_and_quality(self):
        """data_types is a comma separated string of the available
        data types."""
        self.organisation.data_stats = {
            'count_measurement_level': 1,
            'count_measurement_quality': 1,
        }
        self.organisation.save()
        data = self.serialize()
        self.assertEqual(
            data['data_types'], 'Groundwater levels, Groundwater quality'
        )

    def test_time_range_from_date_range(self):
        """time_range reflects the stored date range when not from
        API."""
        self.organisation.data_date_start = datetime.date(2020, 1, 1)
        self.organisation.data_date_end = datetime.date(2021, 6, 1)
        self.organisation.save()
        data = self.serialize()
        self.assertEqual(data['time_range'], 'start: 2020-01; end: 2021-06')

    def test_time_range_from_api(self):
        """time_range shows the API indicator when data_is_from_api is
        True."""
        self.organisation.data_is_from_api = True
        self.organisation.save()
        data = self.serialize()
        self.assertEqual(
            data['time_range'], 'Updated automatically (via API) '
        )

    def test_station_counts_from_data_stats(self):
        """Station and spring counts are read from data_stats."""
        self.organisation.data_stats = {
            'count_well': 5,
            'count_well_with_level': 3,
            'count_well_with_quality': 2,
            'count_spring': 1,
        }
        self.organisation.save()
        data = self.serialize()
        self.assertEqual(data['count_stations'], 5)
        self.assertEqual(data['count_stations_level'], 3)
        self.assertEqual(data['count_stations_quality'], 2)
        self.assertEqual(data['count_springs'], 1)