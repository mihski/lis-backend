from rest_framework import mixins, viewsets, authentication, permissions, decorators, response

from lessons.models import Lesson, Unit, Quest, Course
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
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = Course.objects.all()
    serializer_class = CourseSerializer


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
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

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
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UnitEditorViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, редактирование, получение юнитов
    Если передать x, y - будет отредактирован блок для юнита
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class EditorSessionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = EditorSession.objects.all()
    serializer_class = EditorSessionSerializer
    filterset_fields = ('local_id', )

    def get_user_session_query(self, request):
        user_editor_session_query = EditorSession.objects.filter(
            user=request.user,
            course__id=request.data["course"],
        )

        if "local_id" in request.data:
            user_editor_session_query = user_editor_session_query.filter(local_id=request.data["local_id"])

        return user_editor_session_query.first()

    def create(self, request, *args, **kwargs):
        user_editor_session_query = self.get_user_session_query(request)

        if user_editor_session_query:
            user_editor_session_query.delete()

        return super().create(request, *args, **kwargs)
