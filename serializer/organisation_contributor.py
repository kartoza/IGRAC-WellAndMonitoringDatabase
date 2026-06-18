from rest_framework import serializers

from gwml2.models.well_management.organisation import Organisation


class OrganisationContributorSerializer(serializers.ModelSerializer):
    """Organisation Contributor Serializer."""

    links = serializers.SerializerMethodField()
    data_types = serializers.SerializerMethodField()
    count_stations = serializers.SerializerMethodField()
    count_stations_level = serializers.SerializerMethodField()
    count_stations_quality = serializers.SerializerMethodField()
    count_springs = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = [
            'name', 'description', 'links', 'data_types', 'time_range',
            'license_data', 'count_stations', 'count_stations_level',
            'count_stations_quality', 'count_springs',
        ]

    def get_links(self, obj: Organisation):
        """ Links."""
        return [
            {"name": link.name, "url": link.url} for link in
            obj.links.all()
        ]

    def get_data_types(self, obj: Organisation):
        """Get data types."""
        return ', '.join(obj.data_types)

    def get_count_stations(self, obj: Organisation):
        stats = obj.data_stats or {}
        return stats.get('count_well', 0)

    def get_count_stations_level(self, obj: Organisation):
        stats = obj.data_stats or {}
        return stats.get('count_well_with_level', 0)

    def get_count_stations_quality(self, obj: Organisation):
        stats = obj.data_stats or {}
        return stats.get('count_well_with_quality', 0)

    def get_count_springs(self, obj: Organisation):
        stats = obj.data_stats or {}
        return stats.get('count_spring', 0)
