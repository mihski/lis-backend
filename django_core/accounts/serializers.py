from rest_framework import serializers

from accounts.models import (
    User,
    Profile,
    Statistics,
    ProfileAvatarHead,
    ProfileAvatarClothes,
    ProfileAvatarBrows,
    ProfileAvatarFace,
    ProfileAvatarHair
)
from accounts.tasks import generate_profile_images
from lessons.exceptions import NPCIsNotScientificDirectorException
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
    scientific_director = serializers.PrimaryKeyRelatedField(queryset=NPC.objects.filter(is_scientific_director=True))
    head_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarHead.objects.all())
    hair_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarHair.objects.all())
    face_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarFace.objects.all())
    brows_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarBrows.objects.all())
    cloth_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarClothes.objects.all())
    usual_image = serializers.ImageField(read_only=True)
    angry_image = serializers.ImageField(read_only=True)
    fair_image = serializers.ImageField(read_only=True)
    happy_image = serializers.ImageField(read_only=True)

    isu = serializers.ReadOnlyField(source="user.username")
    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")
    middle_name = serializers.ReadOnlyField(source="user.middle_name")

    def validate_scientific_director(self, scientific_director: NPC) -> NPC:
        if not scientific_director.is_scientific_director:
            raise NPCIsNotScientificDirectorException("NPC is not scientific director")

        return scientific_director

    def _is_avatar_updated(self, instance: Profile, validated_data: dict) -> bool:
        for key in validated_data:
            if key.endswith('_form') and validated_data[key] != getattr(instance, key):
                return True

        return False

    def update(self, instance, validated_data):
        is_avatar_updated = self._is_avatar_updated(instance, validated_data)

        instance = super().update(instance, validated_data)
        instance.save()

        if is_avatar_updated:
            generate_profile_images.delay(instance.id)

        return instance

    class Meta:
        model = Profile
        fields = [
            "id", "isu", "username", "first_name", "last_name", "middle_name",
            "gender", "scientific_director", "university_position", "laboratory",
            "head_form", "hair_form", "face_form", "brows_form", "cloth_form",
            "usual_image", "angry_image", "fair_image", "happy_image",
        ]


class ProfileSerializerWithoutLookForms(ProfileSerializer):
    name = serializers.CharField(source="username")
    usual_image = serializers.ImageField(read_only=True)
    angry_image = serializers.ImageField(read_only=True)
    fair_image = serializers.ImageField(read_only=True)
    happy_image = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "name", "gender", "scientific_director",
            "usual_image", "angry_image", "fair_image", "happy_image",
        ]


class ProfileHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarHead
        fields = "__all__"


class ProfileHairSerializer(serializers.ModelSerializer):
    front_part = serializers.ImageField(read_only=True)
 
    class Meta:
        model = ProfileAvatarHair
        fields = "__all__"


class ProfileFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarFace
        fields = "__all__"


class ProfileClothesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarClothes
        fields = "__all__"


class ProfileBrowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarBrows
        fields = "__all__"
