from rest_framework import serializers

from gwml2.models.well_management.organisation import Organisation


class OrganisationContributorSerializer(serializers.ModelSerializer):
    """Organisation Contributor Serializer."""

    links = serializers.SerializerMethodField()
    data_types = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = [
            'name', 'description', 'links', 'data_types', 'time_range',
            'license_data'
        ]

    def get_links(self, obj: Organisation):
        """ Links."""

        return [
            {"name": link.name, "url": link.url} for link in
            obj.links.all()
        ]

    def get_data_types(self, obj: Organisation):
        """Get data types."""

        return ','.join(obj.data_types)
