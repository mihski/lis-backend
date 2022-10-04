from rest_framework import serializers

from lessons.models import NPC, Location, Lesson, Unit


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPC
        fields = "__all__"


class LocationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class UnitDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")

    class Meta:
        model = Unit
        fields = ["id", "type", "content"]


class LessonDetailSerializer(serializers.ModelSerializer):
    # TODO: переделать
    lesson_name = serializers.CharField(source="name")
    lesson_number = serializers.IntegerField(default=0)
    quest_number = serializers.IntegerField(default=0)
    tasks = serializers.IntegerField(default=0)

    class Meta:
        model = Lesson
        fields = ["lesson_name", "lesson_number", "quest_number", "tasks"]
