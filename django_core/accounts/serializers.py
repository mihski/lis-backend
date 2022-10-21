from rest_framework import serializers, validators

from accounts.models import User, Profile, Statistics
from lessons.models import NPC
from resources.exceptions import NegativeResourcesException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone",
            "first_name", "last_name", "middle_name"
        ]
        read_only_fields = ["id", "username", "email", "phone"]
        ref_name = "lis_user"


class ProfileStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ["quests_done", "lessons_done", "total_time_spend"]


class ProfileStatisticsUpdateSerializer(serializers.Serializer):
    quests_done = serializers.IntegerField(default=0)
    lessons_done = serializers.IntegerField(default=0)
    total_time_spend = serializers.IntegerField(default=0)

    def validate_total_time_spend(self, value: int) -> int:
        if value < 0:
            raise NegativeResourcesException("Time is not supposed to be decreased")
        return value

    def update(self, instance: Statistics, validated_data: dict) -> Statistics:
        instance.quests_done += validated_data["quests_done"]
        instance.lessons_done += validated_data["lessons_done"]
        instance.total_time_spend += validated_data["total_time_spend"]
        instance.save()
        return instance

    class Meta:
        model = Statistics
        fields = ["quests_done", "lessons_done", "total_time_spend"]


class ProfileSerializer(serializers.ModelSerializer):
    scientific_director = serializers.PrimaryKeyRelatedField(queryset=NPC.objects.all())

    def validate_scientific_director(self, scientific_director: NPC) -> NPC:
        if not scientific_director.is_scientific_director:
            raise validators.ValidationError("Is invalid NPC. Should be scientific director")

        return scientific_director

    class Meta:
        model = Profile
        fields = [
            "id", "first_name", "last_name", "middle_name",
            "gender", "scientific_director", "head_form",
            "face_form", "hair_form", "dress_form", "statistics"
        ]


class ProfileSerializerWithoutLookForms(ProfileSerializer):
    name = serializers.CharField(source="first_name")

    class Meta:
        model = Profile
        fields = ["id", "name", "gender", "scientific_director"]
