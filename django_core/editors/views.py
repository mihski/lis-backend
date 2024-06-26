from rest_framework import mixins, viewsets, authentication, permissions, decorators, response, exceptions
from django_filters import rest_framework as filters

from lessons.models import Lesson, Unit, Quest, Course, LessonBlock
from editors.filters import EditorSessionFilter
from editors.serializers import (
    LessonSerializer,
    UnitSerializer,
    QuestSerializer,
    CourseSerializer,
    EditorSessionSerializer
)
from editors.models import EditorSession


class CourseViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, реадктивание и получение курсов
    """
#    authentication_classes = [authentication.SessionAuthentication]
#    permission_classes = [permissions.IsAdminUser]

    queryset = Course.objects.prefetch_related("lessons", "quests", "lessons__unit_set")
    serializer_class = CourseSerializer

    @decorators.action(methods=["GET"], detail=True, url_path='locale')
    def get_locale(self, request, pk, *args, **kwargs):
        course = Course.objects.get(pk=pk)
        return response.Response(course.locale)

    def update(self, request, *args, **kwargs):
        course = self.get_object()

        if not course.is_editable:
            raise exceptions.NotAcceptable("Курс нельзя редактировать")

        if not EditorSession.objects.filter(
                user=request.user,
                course__id=course.id,
                local_id='',
                is_closed=False
        ).exists():
            raise exceptions.PermissionDenied()

        return super().update(request, *args, **kwargs)


class QuestViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, редактирование, получение квестов
    Если передать x, y - будет отредактирован блок для квеста
    При создании нужно передать список id уроков, при получении вернутся сериализованные уроки.
    Нельзя изменить контент внутренних уроков.
    """
  #  authentication_classes = [authentication.SessionAuthentication]
  #  permission_classes = [permissions.IsAdminUser]

    queryset = Quest.objects.all()
    serializer_class = QuestSerializer


class LessonEditorViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, редактирование, получение уроков
    Если передать x, y - будет отредактирован блок для урока
    Если при редактировании передать blocks, то контент юнитов соответственно будет обновлен.
    """
 #   authentication_classes = [authentication.SessionAuthentication]
 #   permission_classes = [permissions.IsAdminUser]

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def update(self, request, *args, **kwargs):
        lesson = self.get_object()

        if not EditorSession.objects.filter(
                user=request.user,
                course__id=lesson.course.id,
                local_id=lesson.local_id,
                is_closed=False
        ).exists():
            raise exceptions.PermissionDenied()

        return super().update(request, *args, **kwargs)


class UnitEditorViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, редактирование, получение юнитов
    Если передать x, y - будет отредактирован блок для юнита
    """
#    authentication_classes = [authentication.SessionAuthentication]
#    permission_classes = [permissions.IsAdminUser]

    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class EditorSessionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
 #   authentication_classes = [authentication.SessionAuthentication]
 #   permission_classes = [permissions.IsAdminUser]

    queryset = EditorSession.objects.all()
    serializer_class = EditorSessionSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EditorSessionFilter

    def get_session_query(self, request):
        user_editor_session_query = EditorSession.objects.filter(course__id=request.data["course"], is_closed=False)

        local_id = request.data.get('local_id', '')

        user_editor_session_query = user_editor_session_query.filter(local_id=local_id)

        return user_editor_session_query

    def get_user_session(self, request):
        qs = self.get_session_query(request)
        return qs.filter(user=request.user, is_closed=False).first()

    def create(self, request, *args, **kwargs):
        already_exists_session_query = self.get_session_query(request)
        user_editor_session = self.get_user_session(request)

        if already_exists_session_query.exists() and not user_editor_session:
            return response.Response(
                EditorSessionSerializer(already_exists_session_query.first()).data,
                status=400,
            )

        if user_editor_session:
            user_editor_session.is_closed = True
            user_editor_session.save()

        return super().create(request, *args, **kwargs)

    @decorators.action(methods=["POST"], detail=False, url_path='end_session')
    def end_session(self, request, *args, **kwargs):
        user_editor_session = self.get_user_session(request)

        if not user_editor_session:
            return response.Response(
                {"detail": {"user": "there is no session for user"}},
                status=400
            )

        user_editor_session.is_closed = True
        user_editor_session.save()

        return response.Response({"status": "ok"})

    @decorators.action(methods=["POST"], detail=False, url_path='my_active_sessions')
    def my_active_sessions(self, request, *args, **kwargs):
        
        user_sessions = EditorSession.objects.filter(pk=2827, is_closed=False)

        return response.Response({
            'sessions': EditorSessionSerializer(user_sessions, many=True).data
        })

    @decorators.action(methods=["POST"], detail=False, url_path='lesson/copy/(?P<pk>[^/.]+)')
    def copy_lesson(self, request, pk=None):
        original_lesson = Lesson.objects.get(pk=pk)
        original_lesson_block = LessonBlock.objects.get(pk=original_lesson.content.pk)
        new_lesson_block = LessonBlock.objects.create(
            entry=original_lesson_block.entry,
            markup=original_lesson_block.markup,
            locale=original_lesson_block.locale
        )
        new_lesson = Lesson.objects.create(
            course=original_lesson.course,
            quest=original_lesson.quest,
            laboratory=original_lesson.laboratory,
            name=original_lesson.name,
            description=original_lesson.description,
            for_gender=original_lesson.for_gender,
            time_cost=original_lesson.time_cost,
            money_cost=original_lesson.money_cost,
            energy_cost=original_lesson.energy_cost,
            has_bonuses=original_lesson.has_bonuses,
            bonuses=original_lesson.bonuses,
            content=new_lesson_block,
            next=original_lesson.next,
            profile_affect=original_lesson.profile_affect,
        )
        return response.Response({
            'lesson': LessonSerializer(new_lesson).data
        })
