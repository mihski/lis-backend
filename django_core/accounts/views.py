from typing import Any

from rest_framework import viewsets, mixins, permissions, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request

from accounts.models import Profile
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
    queryset = Profile.objects.select_related(
        "head_form",
        "cloth_form",
        "face_form",
        "hair_form",
        "brows_form",
        "user",
    ).all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        return self.request.user.profile.get()


class ProfileStatisticsViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileStatisticsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args: tuple, **kwargs: dict) -> Any:
        if self.request.method == "PATCH":
            return ProfileStatisticsUpdateSerializer(*args, **kwargs)
        return ProfileStatisticsSerializer(*args, **kwargs)

    @decorators.action(methods=["GET"], detail=False, url_path="statistics")
    def retrieve_statistics(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile_statistics = request.user.profile.get().statistics  # TODO: select_related("statistics") ?
        serializer: ProfileStatisticsSerializer = self.get_serializer(instance=profile_statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(methods=["PATCH"], detail=False, url_path="statistics/update")
    def update_statistics(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile_statistics = request.user.profile.get().statistics # TODO: select_related("statistics") ?
        serializer: ProfileStatisticsUpdateSerializer = self.get_serializer(
            instance=profile_statistics,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
