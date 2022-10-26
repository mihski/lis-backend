import datetime as dt

from rest_framework import serializers
from django.conf import settings

from resources.exceptions import NegativeResourcesException, ResourcesOverfillException
from resources.models import Resources
from resources.utils import get_max_energy_by_position


class ResourcesSerializer(serializers.ModelSerializer):
    """
        Сериализатор для отображения данных о ресурсах
    """
    timeAmount = serializers.SerializerMethodField(method_name="get_time_amount_timestamp")
    moneyAmount = serializers.ReadOnlyField(source="money_amount", default=0)
    energyAmount = serializers.ReadOnlyField(source="energy_amount", default=0)
    maxEnergyAmount = serializers.SerializerMethodField(method_name="get_max_energy")
    ultimateCost = serializers.IntegerField(default=2500)
    ultimateEnd = serializers.SerializerMethodField(method_name="get_ultimate_end")

    def get_time_amount_timestamp(self, instance: Resources) -> int:
        time_delta = dt.timedelta(days=instance.time_amount)
        course_start_date = settings.START_COURSE_DATE
        course_current_date = course_start_date + time_delta
        return int(course_current_date.timestamp()) * 1000

    def get_max_energy(self, instance: Resources) -> int:
        position = instance.user.university_position
        return get_max_energy_by_position(position)

    def get_ultimate_end(self, instance: Resources) -> int:
        end_datetime = instance.user.ultimate_finish_datetime
        return end_datetime or int(end_datetime.timestamp()) * 1000

    class Meta:
        model = Resources
        fields = [
            "id",
            "timeAmount",
            "moneyAmount",
            "energyAmount",
            "maxEnergyAmount",
            "ultimateCost",
            "ultimateEnd"
        ]


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
