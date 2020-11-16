from rest_framework import serializers
from gwml2.models.well import WellYieldMeasurement, WellQualityMeasurement, WellLevelMeasurement
from gwml2.serializer.general import WellSerializer


class MeasurementSerializer(WellSerializer, serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    def get_time(self, obj):
        if obj.time:
            return obj.time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ''

    class Meta:
        abstract = True
        fields = ['id', 'time', 'parameter', 'methodology']

    def to_representation(self, instance):
        """ Custom representation on the result
        """
        result = super(MeasurementSerializer, self).to_representation(instance)
        result.update(self.quantity('value', instance.value))
        return result


class WellYieldMeasurementSerializer(MeasurementSerializer):
    class Meta:
        model = WellYieldMeasurement
        fields = ['id', 'time', 'parameter', 'methodology']


class WellQualityMeasurementSerializer(MeasurementSerializer):
    class Meta:
        model = WellQualityMeasurement
        fields = ['id', 'time', 'parameter', 'methodology']


class WellLevelMeasurementSerializer(MeasurementSerializer):
    class Meta:
        model = WellLevelMeasurement
        fields = ['id', 'time', 'parameter', 'methodology']
