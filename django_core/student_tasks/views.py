from rest_framework import viewsets, mixins, permissions, response

from lessons.models import Unit
from student_tasks.models import StudentTaskAnswer
from student_tasks.serializers import StudentTaskAnswerSerializer


class StudentTaskViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = StudentTaskAnswer
    serializer = StudentTaskAnswerSerializer

    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        instance = StudentTaskAnswer.objects.filter(
            user=self.request.user,
            task__id=self.kwargs['pk']
        ).first()

        if not instance:
            instance = StudentTaskAnswer.objects.create(
                user=self.request.user,
                task=Unit.objects.filter(id=self.kwargs['pk'])
            )

        return instance
