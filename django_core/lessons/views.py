from rest_framework import viewsets, status
from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from lessons.models import NPC, Location, Lesson, Unit
from lessons.serializers import NPCSerializer, LocationSerializer, LessonSerializer
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
        lesson = self.get_queryset()
        from_unit_id = request.GET.get("from_unit_id", None)

        player = ProfileSerializer(Profile.objects.get(user=request.user))
        units = LessonUnitsTree(lesson, from_unit_id).get_queryset()  # List[Unit]
        serializer = LessonSerializer(lesson)  # <- lesson info, player info, units info
        return Response(serializer.data, status=status.HTTP_200_OK)
