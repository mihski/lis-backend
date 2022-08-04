from rest_framework import viewsets

from lessons.models import Lesson, Unit, Quest, Course
from editors.serializers import LessonSerializer, UnitSerializer, QuestSerializer, CourseSerializer


class LessonEditorViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UnitEditorViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
