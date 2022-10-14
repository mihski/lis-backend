from rest_framework import serializers

from resources.exceptions import NegativeResourcesException
from resources.models import Resources


class ResourcesSerializer(serializers.ModelSerializer):
    """
        Сериализатор для отображения данных о ресурсах
    """
    timeAmount = serializers.IntegerField(source='time_amount')
    moneyAmount = serializers.IntegerField(source='money_amount')
    energyAmount = serializers.IntegerField(source='energy_amount')

    class Meta:
        model = Resources
        fields = ["id", "timeAmount", "moneyAmount", "energyAmount"]


class ResourcesUpdateSerializer(serializers.Serializer):
    """
        Сериализатор для обновления ресурсов
    """
    timeDelta = serializers.IntegerField(default=0)
    moneyDelta = serializers.IntegerField(default=0)
    energyDelta = serializers.IntegerField(default=0)

    def create(self, validated_data):
        pass

    def __validate_fields(self, field_value, field_name, value):
        if field_value + value < 0:
            raise NegativeResourcesException(f"{field_name} is not supposed to be negative")

    def validate_moneyDelta(self, value: int):
        instance: Resources = self.instance
        self.__validate_fields(
            field_value=instance.money_amount,
            field_name="Money", value=value
        )
        return value

    def validate_energyDelta(self, value: int):
        instance: Resources = self.instance
        self.__validate_fields(
            field_value=instance.energy_amount,
            field_name="Energy", value=value
        )
        return value

    def validate_timeDelta(self, value: int) -> int:
        if value < 0:
            raise NegativeResourcesException("Time is not supposed to be decreased")
        return value

    def update(self, instance: Resources, validated_data) -> Resources:
        instance.time_amount += validated_data["timeDelta"]
        instance.energy_amount += validated_data["energyDelta"]
        instance.money_amount += validated_data["moneyDelta"]
        instance.save()
        return instance
