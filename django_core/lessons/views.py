from rest_framework import (
    viewsets,
    permissions,
    authentication,
    mixins,
    decorators,
    status,
    views,
    validators
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.db import transaction

from accounts.models import Profile
from accounts.serializers import ProfileSerializerWithoutLookForms
from lessons.models import (
    NPC,
    Location,
    Lesson,
    Course,
    Branching,
    Review,
    Question,
    ProfileLessonDone,
    Unit
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
from lessons.utils import process_affect
from lessons.exceptions import BranchingAlreadyChosenException
from helpers.lesson_tree import LessonUnitsTree
from helpers.course_tree import CourseLessonsTree
from resources.exceptions import NotEnoughEnergyException, NotEnoughMoneyException
from resources.models import EmotionData
from resources.utils import check_ultimate_is_active


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
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "local_id"

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return BranchingSelectSerializer
        return BranchingDetailSerializer

    @swagger_auto_schema(responses={
        status.HTTP_400_BAD_REQUEST: f"{BranchingAlreadyChosenException.default_code}, {NotEnoughMoneyException.default_code}",
    })
    def update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_400_BAD_REQUEST: BranchingAlreadyChosenException.default_code})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class LessonDetailViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = LessonDetailSerializer
    queryset = Lesson.objects.select_related("course", "quest", "content")
    authentication_classes = [JWTAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "local_id"

    def _check_is_enough_energy(self, profile: Profile, lesson: Lesson) -> bool:
        if (
            check_ultimate_is_active(profile)
            or not settings.CHECK_ENERGY_ON_LESSON_ENTER
        ):
            return True
        return profile.resources.energy_amount >= lesson.energy_cost

    @swagger_auto_schema(
        responses={
            status.HTTP_400_BAD_REQUEST: NotEnoughEnergyException.default_code,
        }
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson = self.get_object()
        from_unit_id = request.GET.get("from_unit_id", None)

        profile: Profile = request.user.profile.get()
        player = ProfileSerializerWithoutLookForms(profile, context={"request": request})

        if not self._check_is_enough_energy(profile, lesson):
            raise NotEnoughEnergyException("Not enough energy to enter lesson")

        unit_tree = LessonUnitsTree(lesson)
        course_tree = CourseLessonsTree(lesson.course)

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
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "local_id"

    def _get_scientific_bonuses(self, profile: Profile, lesson: Lesson) -> tuple[int, int]:
        s_bonuses = lesson.bonuses.get(str(profile.scientific_director_id), {})

        return s_bonuses.get("energy", 0), s_bonuses.get("money", 0)

    def _calculate_resources(self, profile: Profile, lesson: Lesson, salary: int = 0) -> None:
        resources = profile.resources

        if not check_ultimate_is_active(profile):
            resources.energy_amount -= lesson.energy_cost

        s_energy, s_money = self._get_scientific_bonuses(profile, lesson)

        resources.energy_amount += s_energy
        resources.money_amount += salary + s_money
        resources.time_amount += lesson.time_cost
        resources.save()

    def _calculate_statistic(self, profile: Profile, lesson: Lesson, duration: int) -> None:
        statistics = profile.statistics
        statistics.total_time_spend += duration
        statistics.save()

    def _create_emotion(self, profile: Profile, lesson: Lesson, emotion: dict) -> None:
        EmotionData.objects.create(
            emotion=emotion["emotion"],
            comment=emotion["comment"],
            profile=profile,
            lesson=lesson
        )

    @decorators.action(methods=["POST"], detail=True, url_path="finish")
    def finish_lesson(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        lesson: Lesson = self.get_object()
        profile = request.user.profile.get()

        lesson_finish_data = self.serializer_class(lesson, context={"profile": profile}).data

        if ProfileLessonDone.objects.filter(lesson=lesson, profile=profile).exists():
            return Response(lesson_finish_data, status=status.HTTP_200_OK)

        with transaction.atomic():
            self._calculate_resources(profile, lesson, salary=lesson_finish_data["salary_amount"])
            self._calculate_statistic(profile, lesson, duration=int(request.data["duration"]))
            self._create_emotion(profile, lesson, emotion=request.data["emotion"])
            ProfileLessonDone.objects.create(profile=profile, lesson=lesson)

        return Response(lesson_finish_data, status=status.HTTP_200_OK)


class CallbackAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        block = Unit.objects.filter(local_id=pk).first()

        if not block:
            raise validators.ValidationError(f"There is no unit with {block.local_id}")

        affect = block.profile_affect
        process_affect(affect, request.user.profile.first())

        return Response({"status": "ok"})
