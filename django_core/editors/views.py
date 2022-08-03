from rest_framework import viewsets

from lessons.models import Lesson, Unit
from editors.serializers import LessonSerializer, UnitSerializer


class LessonEditorViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class UnitEditorViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
