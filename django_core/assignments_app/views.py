from rest_framework import viewsets, mixins, permissions

from accounts.models import Profile
from .models import Assignment, StudentAssignment
from .serializers import AssignmentSerializer, StudentAssignmentSerializer


class AssignmentListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = (permissions.IsAuthenticated,)


class StudentAssignmentViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin
):
    queryset = StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile: Profile = self.request.user.profile.first()
        return self.queryset.filter(profile=profile)
