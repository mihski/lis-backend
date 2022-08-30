from rest_framework import viewsets, mixins, decorators

from student_tasks.models import StudentTaskAnswer
from student_tasks.serializers import StudentTaskAnswerSerializer


class StudentTaskViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = StudentTaskAnswer
    serializer = StudentTaskAnswerSerializer

    lookup_field = 'unit__id'
