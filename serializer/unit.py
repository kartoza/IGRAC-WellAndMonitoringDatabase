from rest_framework import serializers
from gwml2.models.general import Unit, UnitConvertion


class UnitSerializer(serializers.ModelSerializer):
    to = serializers.SerializerMethodField()

    def get_to(self, obj):
        """ Conversion from this unit
        :param obj:
        :type obj: Unit
        """

        return {conversion.unit_to.name: conversion.formula for conversion in UnitConvertion.objects.filter(unit_from=obj)}

    class Meta:
        model = Unit
        fields = ['id', 'name', 'to']
