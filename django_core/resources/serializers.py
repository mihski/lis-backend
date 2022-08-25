from rest_framework import serializers
from resources.models import Resources


class ResourcesSerializer(serializers.ModelSerializer):
    timeAmount = serializers.IntegerField(source='time_amount')
    moneyAmount = serializers.IntegerField(source='money_amount')
    energyAmount = serializers.IntegerField(source='energy_amount')

    class Meta:
        model = Resources
        fields = ["id", "timeAmount", "moneyAmount", "energyAmount"]
