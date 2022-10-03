from rest_framework import serializers

from accounts.serializers import ProfileSerializer
from lessons.models import NPC, Location, Lesson, Unit


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPC
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ["local_id", "type", "next", "content"]

    def content(self, obj):
        pass


class LessonSerializer(serializers.ModelSerializer):
    # player = ProfileSerializer()  # кроме custom персонажа
    location = LocationSerializer()
    locales = serializers.JSONField()

    location = serializers.SerializerMethodField()
    npc = serializers.SerializerMethodField()
    # TODO: переделать
    lesson_number = serializers.IntegerField(default=0)
    quest_number = serializers.IntegerField(default=0)
    tasks = serializers.IntegerField(default=0)
    # chunk = UnitSerializer(many=True)
    # location and npc - first in units -> ids -> unit content

    class Meta:
        model = Lesson
        fields = ["name", "location__npc_uid"]
        # exclude = ["player_head_form", "player_face_form", "player_hair_form", "player_dress_form"]

    def location(self, obj):
        pass

    def npc(self, obj):
        pass
