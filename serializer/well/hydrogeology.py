from rest_framework import serializers
from gwml2.models.hydrogeology import HydrogeologyParameter, PumpingTest
from gwml2.serializer.general import WellSerializer


class PumpingTestSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = PumpingTest
        fields = ['porosity', 'specific_yield', 'storativity', 'test_type']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: PumpingTest
        """
        result = super(PumpingTestSerializer, self).to_representation(instance)
        result.update(self.quantity('specific_capacity', instance.specific_capacity))
        result.update(self.quantity('transmissivity', instance.transmissivity))
        result.update(self.quantity('specific_storage', instance.specific_storage))
        return result


class HydrogeologyParameterSerializer(WellSerializer, serializers.ModelSerializer):
    pumping_test = serializers.SerializerMethodField()

    def get_pumping_test(self, obj):
        """ Return water strike list
        :param obj:
        :type obj: HydrogeologyParameter
        """
        return PumpingTestSerializer(obj.pumping_test).data

    class Meta:
        model = HydrogeologyParameter
        fields = ['aquifer_name', 'aquifer_material', 'aquifer_type', 'confinement', 'degree_of_confinement', 'pumping_test']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: HydrogeologyParameter
        """
        result = super(HydrogeologyParameterSerializer, self).to_representation(instance)
        result.update(self.quantity('aquifer_thickness', instance.aquifer_thickness))
        return result
