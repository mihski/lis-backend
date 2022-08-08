from rest_framework import viewsets

from lessons.models import Lesson, Unit, Quest, Course
from editors.serializers import LessonSerializer, UnitSerializer, QuestSerializer, CourseSerializer


class LessonEditorViewSet(viewsets.ModelViewSet):
    """ Создание, редактирование, получение уроков
    Если передать x, y - будет отредактирован блок для урока
    Если при редактировании передать blocks, то контент юнитов соответственно будет обновлен.
    """
    # TODO: add filter by course_id
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UnitEditorViewSet(viewsets.ModelViewSet):
    """ Создание, редактирование, получение юнитов
    Если передать x, y - будет отредактирован блок для юнита
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class QuestViewSet(viewsets.ModelViewSet):
    """ Создание, редактирование, получение квестов
    Если передать x, y - будет отредактирован блок для квеста
    При создании нужно передать список id уроков, при получении вернутся сериализованные уроки.
    """
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ Создание, реадктивание и получение курсов
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
