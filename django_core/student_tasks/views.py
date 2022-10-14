from rest_framework import viewsets, mixins, permissions, validators

from accounts.models import Profile
from lessons.models import Unit
from student_tasks.models import StudentTaskAnswer
from student_tasks.serializers import StudentTaskAnswerSerializer


class StudentTaskViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = StudentTaskAnswer.objects.all()
    serializer_class = StudentTaskAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        unit = Unit.objects.filter(local_id=self.kwargs['pk']).first()

        if not unit:
            raise validators.ValidationError(f"There is no unit with id {self.kwargs['pk']}")

        profile, created = Profile.objects.get_or_create(user=self.request.user)
        instance, created = StudentTaskAnswer.objects.get_or_create(
            profile=profile,
            task=unit
        )

        return instance
