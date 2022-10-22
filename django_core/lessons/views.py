from rest_framework import viewsets, permissions, authentication, mixins, decorators, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile, Statistics
from accounts.serializers import ProfileSerializerWithoutLookForms
from accounts.permissions import HasProfilePermission
from lessons.models import (
    NPC,
    Location,
    Lesson,
    Course,
    Branching,
    Review,
    Question,
    ProfileLessonDone
)
from lessons.serializers import (
    NPCSerializer,
    LocationDetailSerializer,
    LessonDetailSerializer,
    CourseMapSerializer,
    BranchingSelectSerializer,
    BranchingDetailSerializer,
    QuestionSerializer,
    ReviewSerializer,
    LessonFinishSerializer,
)
from helpers.lesson_tree import LessonUnitsTree
from helpers.course_tree import CourseLessonsTree


class NPCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = NPCSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationDetailSerializer


class CourseMapViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Course.objects.prefetch_related(
        "lessons", "quests", "branchings",
        "quests__lessons", "quests__branchings",
    )
    serializer_class = CourseMapSerializer
    permission_classes = (permissions.IsAuthenticated, )


class BranchSelectViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Branching.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    lookup_field = "local_id"

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return BranchingSelectSerializer

        return BranchingDetailSerializer


class LessonDetailViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.select_related("course", "quest", "content")
    authentication_classes = [JWTAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "local_id"

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson = self.get_object()
        from_unit_id = request.GET.get("from_unit_id", None)

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

            locales["ru"] = locales.get("ru", {})
            locales["en"] = locales.get("en", {})

            locales["ru"][lesson_name_field] = lesson.course.locale["ru"][lesson_name_field]
            locales["en"][lesson_name_field] = lesson.course.locale["en"][lesson_name_field]

            lesson_data.update({
                "finished": ProfileLessonDone.objects.filter(lesson=lesson, profile=profile).exists(),
                "location": first_location_id or 1,
                "npc": first_npc_id or -1,
                "locales": locales,
                "tasks": unit_tree.task_count,
                "quest_number": course_tree.get_quest_number(profile, lesson),
                "lesson_number": course_tree.get_lesson_number(profile, lesson) - 1,
            })

        data = {**lesson_data, "player": player.data, "chunk": unit_chunk}
        return Response(data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
        ViewSet для обработки поступающих отзывов
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)


class QuestionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
        ViewSet для обработки поступающих вопросов
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LessonActionsViewSet(viewsets.GenericViewSet):
    queryset = Lesson.objects.select_related("course", "quest")
    serializer_class = LessonFinishSerializer
    permission_classes = [permissions.IsAuthenticated, HasProfilePermission]
    lookup_field = "local_id"

    def _take_off_resources(self, profile: Profile, lesson: Lesson) -> None:
        resources = profile.resources
        resources.energy_amount -= lesson.energy_cost
        resources.time_amount += lesson.time_cost
        resources.save()

    def _calculate_statistic(self, profile: Profile, lesson: Lesson) -> None:
        statistics, _ = Statistics.objects.get_or_create(profile=profile)

    @decorators.action(methods=["POST"], detail=True, url_path="finish")
    def finish_lesson(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson: Lesson = self.get_object()
        profile = request.user.profile.prefetch_related("resources").first()

        lesson_finish_data = self.serializer_class(lesson, context={"profile": profile}).data

        if ProfileLessonDone.objects.filter(lesson=lesson, profile=profile).exists():
            return lesson_finish_data

        self._take_off_resources(profile, lesson)
        self._calculate_statistic(profile, lesson)

        lesson_done = ProfileLessonDone.objects.create(profile=profile, lesson=lesson)

        return Response(lesson_finish_data)
