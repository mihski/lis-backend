import datetime

from rest_framework import serializers

from resources.exceptions import NegativeResourcesException, ResourcesOverfillException
from resources.models import Resources
from resources.utils import (
    get_ultimate_remaining_time,
    get_max_energy_by_position
)


class ResourcesSerializer(serializers.ModelSerializer):
    """
        Сериализатор для отображения данных о ресурсах
    """
    timeAmount = serializers.ReadOnlyField(source="time_amount", default=0)
    moneyAmount = serializers.ReadOnlyField(source="money_amount", default=0)
    energyAmount = serializers.ReadOnlyField(source="energy_amount", default=0)
    maxEnergyAmount = serializers.SerializerMethodField(method_name="get_max_energy")
    ultimateEndDateTime = serializers.SerializerMethodField(method_name="get_ultimate_end_dt")

    def get_max_energy(self, instance: Resources) -> int:
        position = instance.user.university_position
        return get_max_energy_by_position(position)

    def get_ultimate_end_dt(self, instance: Resources) -> datetime.datetime:
        profile = instance.user
        return profile.ultimate_finish_datetime

    class Meta:
        model = Resources
        fields = ["id", "timeAmount", "moneyAmount", "energyAmount", "maxEnergyAmount", "ultimateEndDateTime"]


class ResourcesUpdateSerializer(serializers.Serializer):
    """
        Сериализатор для обновления ресурсов
    """
    timeDelta = serializers.IntegerField(default=0)
    moneyDelta = serializers.IntegerField(default=0)
    energyDelta = serializers.IntegerField(default=0)

    def validate_timeDelta(self, value: int) -> int:
        if value < 0:
            raise NegativeResourcesException("Time is not supposed to be decreased")
        return value

    def validate_moneyDelta(self, value: int) -> int:
        if self.instance.money_amount + value < 0:
            raise NegativeResourcesException("Money is not supposed to be decreased")
        return value

    def validate_energyDelta(self, value: int) -> int:
        instance = self.instance
        position = instance.user.university_position
        max_energy = get_max_energy_by_position(position)

        result = value + instance.energy_amount
        if result < 0:
            raise NegativeResourcesException("Energy is not supposed to be decreased")
        elif result > max_energy:
            raise ResourcesOverfillException("Energy is not supposed to be overfilled")
        return value

    def update(self, instance: Resources, validated_data: dict) -> Resources:
        instance.time_amount += validated_data["timeDelta"]
        instance.energy_amount += validated_data["energyDelta"]
        instance.money_amount += validated_data["moneyDelta"]
        instance.save()
        return instance
