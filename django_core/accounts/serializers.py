from django.conf import settings
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
from resources.utils import check_ultimate_is_active
from lessons.exceptions import NPCIsNotScientificDirectorException, FirstScientificDirectorIsNotDefaultException
from lessons.models import NPC, ProfileLessonDone
from resources.exceptions import NegativeResourcesException, NotEnoughEnergyException
from resources.serializers import EmotionDataSerializer


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
    lessons_done = serializers.SerializerMethodField()
    tasks_done = serializers.SerializerMethodField()
    quests_done = serializers.SerializerMethodField()

    def get_tasks_done(self, statistics: Statistics) -> int:
        return statistics.profile.tasks_done.filter(is_correct=True).count()

    def get_lessons_done(self, statistics: Statistics) -> int:
        return ProfileLessonDone.objects.filter(profile=statistics.profile).count()

    def get_quests_done(self, statistics: Statistics) -> int:
        return ProfileLessonDone.objects.filter(
            lesson__next__in=["", "-1"],
            lesson__quest__isnull=False
        ).count()

    class Meta:
        model = Statistics
        fields = ["lessons_done", "quests_done", "tasks_done", "total_time_spend"]


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


class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPC
        fields = ["id", "uid", "ru_name", "en_name", "usual_image", "angry_image", "fair_image", "sad_image"]


class ProfileSerializer(serializers.ModelSerializer):
    scientific_director = serializers.PrimaryKeyRelatedField(queryset=NPC.objects.all())
    head_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarHead.objects.all())
    hair_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarHair.objects.all())
    face_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarFace.objects.all())
    brows_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarBrows.objects.all())
    cloth_form = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProfileAvatarClothes.objects.all())
    usual_image = serializers.ImageField(read_only=True)
    angry_image = serializers.ImageField(read_only=True)
    fair_image = serializers.ImageField(read_only=True)
    happy_image = serializers.ImageField(read_only=True)

    supervisor = SupervisorSerializer(source="scientific_director")

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

    def _is_enough_energy_to_change_scientific_director(self, instance: Profile) -> bool:
        return (
            check_ultimate_is_active(instance)
            or instance.resources.energy_amount >= settings.CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST
        )

    def _update_scientific_director(self, profile: Profile, data: dict) -> None:
        """
        Случаи смены научника:
            1) NPC -> None -> Lily (0): admin panel only
            2) NPC -> Lily (-6)
            3) NPC -> NPC (-6)
            4) None -> Lily (0)
            5) None -> NPC: forbidden
        """

        if not profile.scientific_director and (
            data["scientific_director"] != NPC.objects.get(uid=settings.DEFAULT_SCIENTIFIC_DIRECTOR_UID)
        ):
            raise FirstScientificDirectorIsNotDefaultException("First scientific director should be default")

        if profile.scientific_director and not self._is_enough_energy_to_change_scientific_director(profile):
            raise NotEnoughEnergyException("It's not possible to change the scientific director")

    def update(self, instance: Profile, validated_data: dict) -> Profile:
        is_avatar_updated = self._is_avatar_updated(instance, validated_data)

        if "scientific_director" in validated_data:
            self._update_scientific_director(instance, validated_data)

        instance = super().update(instance, validated_data)
        instance.save()

        if is_avatar_updated:
            generate_profile_images(instance.id)

        return instance

    class Meta:
        model = Profile
        fields = [
            "id", "isu", "username", "first_name", "last_name", "middle_name",
            "gender", "supervisor", "university_position", "laboratory",
            "head_form", "hair_form", "face_form", "brows_form", "cloth_form",
            "usual_image", "angry_image", "fair_image", "happy_image", "course",
            "scientific_director"
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
            "id", "name", "gender", "scientific_director", "university_position",
            "usual_image", "angry_image", "fair_image", "happy_image",
        ]


class ProfileHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarHead
        fields = ["id", "gender", "usual_part"]


class ProfileHairSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarHair
        fields = ["id", "gender", "color", "front_part", "back_part"]


class ProfileClothesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarClothes
        fields = ["id", "gender", "usual_part"]


class ProfileBrowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarBrows
        fields = ["id", "color", "type", "gender", "usual_part"]


class ProfileFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAvatarFace
        fields = ["id", "gender", "usual_part"]


class ProfileAlbumSerializer(serializers.ModelSerializer):
    statistics = ProfileStatisticsSerializer()
    emotions = EmotionDataSerializer(many=True)

    class Meta:
        model = Profile
        fields = ["id", "isu", "username", "statistics", "emotions"]
