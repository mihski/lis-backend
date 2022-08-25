from rest_framework import serializers
from resources.models import Resources


class ResourcesSerializer(serializers.ModelSerializer):
    timeAmount = serializers.IntegerField(source='time_amount')
    moneyAmount = serializers.IntegerField(source='money_amount')
    energyAmount = serializers.IntegerField(source='energy_amount')

    class Meta:
        model = Resources
        fields = ["id", "timeAmount", "moneyAmount", "energyAmount"]


class ResourcesUpdateSerializer(serializers.Serializer):
    timeDelta = serializers.IntegerField(default=0)
    moneyDelta = serializers.IntegerField(default=0)
    energyDelta = serializers.IntegerField(default=0)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
