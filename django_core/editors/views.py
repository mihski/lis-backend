from rest_framework import mixins, viewsets

from lessons.models import Lesson, Unit, Quest, Course
from editors.serializers import LessonSerializer, UnitSerializer, QuestSerializer, CourseSerializer


class CourseViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, реадктивание и получение курсов
    """
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
    # TODO: add filter by course_id
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UnitEditorViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ Создание, редактирование, получение юнитов
    Если передать x, y - будет отредактирован блок для юнита
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
