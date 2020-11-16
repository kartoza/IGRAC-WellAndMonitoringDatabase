from rest_framework import serializers
from gwml2.models.management import Management, License
from gwml2.serializer.general import WellSerializer


class LicenseSerializer(WellSerializer, serializers.ModelSerializer):
    valid_from = serializers.SerializerMethodField()
    valid_until = serializers.SerializerMethodField()

    def get_valid_from(self, obj):
        if obj.valid_from:
            return obj.valid_from.strftime('%Y-%m-%d')
        else:
            return ''

    def get_valid_until(self, obj):
        if obj.valid_until:
            return obj.valid_until.strftime('%Y-%m-%d')
        else:
            return ''

    class Meta:
        model = License
        fields = ['number', 'valid_from', 'valid_until', 'description']


class ManagementSerializer(WellSerializer, serializers.ModelSerializer):
    pumping_test = serializers.SerializerMethodField()

    def get_pumping_test(self, obj):
        """ Return water strike list
        :param obj:
        :type obj: Management
        """
        return LicenseSerializer(obj.license).data

    class Meta:
        model = Management
        fields = ['organisation', 'manager', 'description', 'groundwater_use', 'number_of_users']
