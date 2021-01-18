from rest_framework import serializers
from gwml2.models.geology import Geology
from gwml2.serializer.general import WellSerializer


class GeologySerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = Geology
        fields = []

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: Geology
        """
        result = super(GeologySerializer, self).to_representation(instance)
        result.update(self.quantity('total_depth', instance.total_depth))
        return result
