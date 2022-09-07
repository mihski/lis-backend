from rest_framework import serializers
from lessons.models import NPC, Location


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPC
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
