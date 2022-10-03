from typing import List

from rest_framework import viewsets, status
from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import ProfileSerializer, ProfileSerializerWithoutLookForms
from lessons.models import NPC, Location, Lesson, Unit
from lessons.serializers import NPCSerializer, LocationSerializer, LessonSerializer, UnitSerializer
from helpers.structures import LessonUnitsTree


class NPCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = NPCSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LessonDetailViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = LessonSerializer

    def get_queryset(self) -> QuerySet[Lesson]:
        qs: QuerySet[Lesson] = Lesson.objects.all()
        lesson = qs.filter(local_id=self.kwargs["lesson_id"])
        return lesson

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson_queryset = self.get_queryset()
        lesson_object: Lesson = lesson_queryset.first()
        from_unit_id = request.GET.get("from_unit_id", None)

        player = ProfileSerializerWithoutLookForms(Profile.objects.get(user=request.user))
        unit_tree = LessonUnitsTree(lesson_queryset, from_unit_id)
        units = unit_tree.get_queryset()
        units = UnitSerializer(units, many=True)

        location_id, npc_id = unit_tree.get_additional_data()
        lesson = LessonSerializer(lesson_object)  # <- lesson info, player info, units info
        lesson_data = lesson.data
        lesson_data.update({
            "location": location_id,
            "npc": npc_id,
            # "locales": lesson_object.content.locale
        })

        data = {'lesson': lesson_data, "player": player.data, "chunk": units.data}

        return Response(data, status=status.HTTP_200_OK)
