from rest_framework import serializers
from gwml2.models.drilling import Drilling, StratigraphicLog, WaterStrike
from gwml2.serializer.general import WellSerializer


class WaterStrikeSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = WaterStrike
        fields = ['id', 'description']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: WaterStrike
        """
        result = super(WaterStrikeSerializer, self).to_representation(instance)
        result.update(self.reference_elevation('depth', instance.depth))
        return result


class StratigraphicLogSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = StratigraphicLog
        fields = ['reference_elevation', 'material', 'stratigraphic_unit']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: StratigraphicLog
        """
        result = super(StratigraphicLogSerializer, self).to_representation(instance)
        result.update(self.quantity('top_depth', instance.top_depth))
        result.update(self.quantity('bottom_depth', instance.bottom_depth))
        return result


class DrillingSerializer(WellSerializer, serializers.ModelSerializer):
    water_strike = serializers.SerializerMethodField()
    stratigraphic_log = serializers.SerializerMethodField()

    def get_water_strike(self, obj):
        """ Return water strike list
        :param obj:
        :type obj: Drilling
        """
        return WaterStrikeSerializer(obj.waterstrike_set.all(), many=True).data

    def get_stratigraphic_log(self, obj):
        """ Return stratigraphic log list
        :param obj:
        :type obj: Drilling
        """
        return StratigraphicLogSerializer(obj.stratigraphiclog_set.all(), many=True).data

    class Meta:
        model = Drilling
        fields = ['drilling_method', 'driller', 'successful', 'cause_of_failure', 'year_of_drilling', 'water_strike', 'stratigraphic_log']
