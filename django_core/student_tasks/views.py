from rest_framework import viewsets, mixins, permissions
from drf_yasg.utils import swagger_auto_schema

from lessons.models import Unit
from lessons.exceptions import UnitNotFoundException
from helpers.swagger_factory import SwaggerFactory
from student_tasks.models import StudentTaskAnswer
from student_tasks.serializers import StudentTaskAnswerSerializer


class StudentTaskViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = StudentTaskAnswer.objects.all()
    serializer_class = StudentTaskAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self) -> StudentTaskAnswer:
        pk = self.kwargs["pk"]

        unit = Unit.objects.filter(local_id=pk)
        if not unit.exists():
            raise UnitNotFoundException(f"Unit with id {pk} not found")

        profile = self.request.user.profile.get()
        instance, created = StudentTaskAnswer.objects.get_or_create(
            profile=profile,
            task=unit.first()
        )

        return instance

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[UnitNotFoundException]
    ))
    def retrieve(self, request, *args, **kwargs):
        return super(StudentTaskViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[UnitNotFoundException]
    ))
    def update(self, request, *args, **kwargs):
        return super(StudentTaskViewSet, self).update(request, *args, **kwargs)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[UnitNotFoundException]
    ))
    def partial_update(self, request, *args, **kwargs):
        return super(StudentTaskViewSet, self).partial_update(request, *args, **kwargs)
