from rest_framework import serializers

from gwml2.models import WellDeletion


class WellDeletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellDeletion
        exclude = ['data', 'ids']
