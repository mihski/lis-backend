from rest_framework import viewsets
from lessons.models import NPC, Location
from lessons.serializers import NPCSerializer, LocationSerializer


class NPCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = NPCSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

