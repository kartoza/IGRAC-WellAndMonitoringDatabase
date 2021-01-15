from rest_framework import serializers
from gwml2.models.general import Unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']
