from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import ProfileSerializerWithoutLookForms
from lessons.models import NPC, Location, Lesson
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
    queryset = Lesson.objects.select_related('course')
    lookup_field = 'local_id'

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson = self.get_object()
        from_unit_id = request.GET.get("from_unit_id", None)

        player = ProfileSerializerWithoutLookForms(Profile.objects.get(user=request.user))

        unit_tree = LessonUnitsTree(lesson)

        lesson_data = LessonSerializer(lesson).data
        lesson_name_field = lesson.local_id + '_name'
        locales = lesson.content.locale
        locales['ru'][lesson_name_field] = lesson.course.locale['ru'][lesson_name_field]
        locales['en'][lesson_name_field] = lesson.course.locale['en'][lesson_name_field]

        lesson_data.update({
            "location": unit_tree.location_id or 1,
            "npc": unit_tree.npc_id or -1,
            "locales": locales,
            "tasks": unit_tree.task_count
        })

        data = {**lesson_data, "player": player.data, "chunk": unit_tree.make_lessons_queue(from_unit_id)}

        return Response(data)
