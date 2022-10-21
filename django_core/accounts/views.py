from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.request import Request

from accounts.models import Profile, Statistics
from accounts.permissions import HasProfilePermission
from accounts.exceptions import StatisticsDoesNotExistException
from accounts.serializers import (
    ProfileSerializer,
    ProfileStatisticsSerializer,
    ProfileStatisticsUpdateSerializer
)


class ProfileViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """ Ручка для работы с профилем персонажа
    Все взаимодействие будет происходить с помощью
    идентификатора пользователя.

    Ошибки:
    - 400 - с тегом "scientific_director", если NPC не может быть научником
    - 403 - если не авторизован или если пытаешься изменить не свой профиль
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        self.check_object_permissions(self.request, profile)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ProfileStatisticsViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    queryset = Profile.objects.all()
    serializer_class = ProfileStatisticsSerializer
    permission_classes = (permissions.IsAuthenticated, HasProfilePermission)
    http_method_names = ["get", "patch"]

    def get_serializer(self, *args: tuple, **kwargs: dict):
        if self.request.method == "PATCH":
            return ProfileStatisticsUpdateSerializer(*args, **kwargs)
        return ProfileStatisticsSerializer(*args, **kwargs)

    def retrieve(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = self.get_object()
        statistics, _ = Statistics.objects.get_or_create(profile=profile)
        serializer: ProfileStatisticsSerializer = self.get_serializer(instance=statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = self.get_object()
        profile_statistics = Statistics.objects.filter(profile=profile)
        if not profile_statistics.exists():
            raise StatisticsDoesNotExistException("Your profile doesn't have any statistics")

        serializer: ProfileStatisticsUpdateSerializer = self.get_serializer(
            instance=profile_statistics.first(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
