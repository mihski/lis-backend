from rest_framework import serializers

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

    class Meta:
        model = Unit
        fields = ["id", "local_id", "type", "next", "content"]


class LessonSerializer(serializers.ModelSerializer):
    # TODO: переделать
    lesson_name = serializers.CharField(source="name")
    lesson_number = serializers.IntegerField(default=0)
    quest_number = serializers.IntegerField(default=0)
    tasks = serializers.IntegerField(default=0)

    class Meta:
        model = Lesson
        fields = ["lesson_name", "lesson_number", "quest_number", "tasks"]
