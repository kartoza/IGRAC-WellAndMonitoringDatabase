from rest_framework import serializers
from gwml2.models.construction import Construction, ConstructionStructure
from gwml2.serializer.general import WellSerializer


class ConstructionStructureSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = ConstructionStructure
        fields = ['id', 'type', 'reference_elevation', 'material', 'description']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: StratigraphicLog
        """
        result = super(ConstructionStructureSerializer, self).to_representation(instance)
        result.update(self.quantity('top_depth', instance.top_depth))
        result.update(self.quantity('bottom_depth', instance.bottom_depth))
        result.update(self.quantity('diameter', instance.diameter))
        return result


class ConstructionSerializer(WellSerializer, serializers.ModelSerializer):
    structure = serializers.SerializerMethodField()

    def get_structure(self, obj):
        """ Return water strike list
        :param obj:
        :type obj: Construction
        """
        return ConstructionStructureSerializer(obj.constructionstructure_set.all(), many=True).data

    class Meta:
        model = Construction
        fields = ['pump_installer', 'pump_description', 'structure']
