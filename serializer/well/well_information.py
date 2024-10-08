from rest_framework import serializers
from gwml2.models.well import Well
from gwml2.serializer.general import WellSerializer
from gwml2.serializer.well.construction import ConstructionSerializer
from gwml2.serializer.well.drilling import DrillingSerializer
from gwml2.serializer.well.geology import GeologySerializer
from gwml2.serializer.well.hydrogeology import HydrogeologyParameterSerializer
from gwml2.serializer.well.management import ManagementSerializer
from gwml2.serializer.well.measurement import (
    WellLevelMeasurementSerializer, WellQualityMeasurementSerializer, WellYieldMeasurementSerializer)


class GeneralInformationSerializer(WellSerializer, serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        """ Return latitude of well
        :param obj:
        :type obj: Well
        """
        if obj.location:
            return round(obj.location.y, 7)
        else:
            return None

    def get_longitude(self, obj):
        """ Return longitude of well
        :param obj:
        :type obj: Well
        """
        if obj.location:
            return round(obj.location.x, 7)
        else:
            return None

    class Meta:
        model = Well
        fields = [
            'original_id', 'organisation', 'name', 'status', 'feature_type',
            'purpose', 'description', 'latitude', 'longitude', 'country', 'address']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: Well
        """
        result = super(GeneralInformationSerializer, self).to_representation(instance)
        result.update(self.quantity('ground_surface_elevation', instance.ground_surface_elevation))
        result.update(self.quantity('top_borehole_elevation', instance.top_borehole_elevation))
        result.update(self.quantity('glo_90m_elevation', instance.glo_90m_elevation))
        return result


class WellLikeFormSerializer(WellSerializer, serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()
    geology = serializers.SerializerMethodField()
    drilling = serializers.SerializerMethodField()
    construction = serializers.SerializerMethodField()
    hydrogeology = serializers.SerializerMethodField()
    management = serializers.SerializerMethodField()

    level_measurement = serializers.SerializerMethodField()
    quality_measurement = serializers.SerializerMethodField()
    yield_measurement = serializers.SerializerMethodField()

    def get_general_information(self, obj):
        """ Return general information of well
        :param obj:
        :type obj: Well
        """
        return GeneralInformationSerializer(obj).data

    def get_geology(self, obj):
        """ Return geology of well
        :param obj:
        :type obj: Well
        """
        return GeologySerializer(obj.geology).data

    def get_drilling(self, obj):
        """ Return drilling of well
        :param obj:
        :type obj: Well
        """
        return DrillingSerializer(obj.drilling).data

    def get_construction(self, obj):
        """ Return construction of well
        :param obj:
        :type obj: Well
        """
        return ConstructionSerializer(obj.construction).data

    def get_hydrogeology(self, obj):
        """ Return hydrogeology of well
        :param obj:
        :type obj: Well
        """
        return HydrogeologyParameterSerializer(obj.hydrogeology_parameter).data

    def get_management(self, obj):
        """ Return management of well
        :param obj:
        :type obj: Well
        """
        return ManagementSerializer(obj.management).data

    def get_level_measurement(self, obj):
        """ Return level_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellLevelMeasurementSerializer(
            obj.welllevelmeasurement_set.all(), many=True).data

    def get_quality_measurement(self, obj):
        """ Return quality_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellQualityMeasurementSerializer(
            obj.wellqualitymeasurement_set.all(), many=True).data

    def get_yield_measurement(self, obj):
        """ Return yield_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellYieldMeasurementSerializer(
            obj.wellyieldmeasurement_set.all(), many=True).data

    class Meta:
        model = Well
        fields = [
            'general_information', 'geology', 'drilling', 'construction',
            'hydrogeology', 'management',
            'level_measurement', 'quality_measurement', 'yield_measurement'
        ]
