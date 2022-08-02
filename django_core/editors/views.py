from rest_framework import viewsets

from lessons.models import Lesson
from editors.serializers import LessonSerializer


class LessonEditorViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
