from rest_framework import viewsets, permissions, authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from accounts.serializers import ProfileSerializerWithoutLookForms
from lessons.models import NPC, Location, Lesson
from lessons.serializers import NPCSerializer, LocationDetailSerializer, LessonDetailSerializer
from helpers.structures import LessonUnitsTree, CourseLessonsTree


class NPCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = NPCSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationDetailSerializer


class LessonDetailViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.select_related('course')
    authentication_classes = [JWTAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'local_id'

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson = self.get_object()
        from_unit_id = request.GET.get('from_unit_id', None)

        unit_tree = LessonUnitsTree(lesson)
        course_tree = CourseLessonsTree(lesson.course)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        player = ProfileSerializerWithoutLookForms(profile)

        first_location_id, first_npc_id, unit_chunk = (
            unit_tree.make_lessons_queue(from_unit_id, hide_task_answers=True)
        )

        lesson_data = {}
        if not from_unit_id:
            lesson_data = LessonDetailSerializer(lesson).data
            lesson_name_field = lesson.name
            locales = lesson.content.locale
            locales['ru'][lesson_name_field] = lesson.course.locale['ru'][lesson_name_field]
            locales['en'][lesson_name_field] = lesson.course.locale['en'][lesson_name_field]

            lesson_data.update({
                'location': first_location_id or 1,
                'npc': first_npc_id or -1,
                'locales': locales,
                'tasks': unit_tree.task_count,
            })

        data = {**lesson_data, 'player': player.data, 'chunk': unit_chunk}

        return Response(data)
