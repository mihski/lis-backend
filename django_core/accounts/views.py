from typing import Any

from rest_framework import viewsets, mixins, permissions, status, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Profile, ProfileAvatarHair, ProfileAvatarFace, ProfileAvatarBrows, ProfileAvatarHead, \
    ProfileAvatarClothes
from accounts.serializers import (
    ProfileSerializer,
    ProfileStatisticsSerializer,
    ProfileStatisticsUpdateSerializer, ProfileHairSerializer, ProfileFaceSerializer, ProfileHeadSerializer,
    ProfileBrowsSerializer, ProfileClothesSerializer
)
from lessons.exceptions import NPCIsNotScientificDirectorException
from resources.exceptions import NegativeResourcesException
from helpers.swagger_factory import SwaggerFactory


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

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[NPCIsNotScientificDirectorException]
    ))
    def update(self, request, *args, **kwargs) -> Response:
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[NPCIsNotScientificDirectorException]
    ))
    def partial_update(self, request, *args, **kwargs) -> Response:
        return super().partial_update(request, *args, **kwargs)


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
        profile_statistics = request.user.profile.get().statistics
        serializer: ProfileStatisticsSerializer = self.get_serializer(instance=profile_statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[NegativeResourcesException]
    ))
    @decorators.action(methods=["PATCH"], detail=False, url_path="statistics/update")
    def update_statistics(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile_statistics = request.user.profile.get().statistics
        serializer: ProfileStatisticsUpdateSerializer = self.get_serializer(
            instance=profile_statistics,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class AvatarViewSet(viewsets.GenericViewSet):
    serializers = [
        ProfileHairSerializer,
        ProfileFaceSerializer,
        ProfileHeadSerializer,
        ProfileBrowsSerializer,
        ProfileClothesSerializer
    ]

    def get_queryset(self):
        return [
            s.Meta.model.objects.all()
            for s in self.serializers
        ]

    def list(self, request, *args, **kwargs):
        c2s = {s.Meta.model: s for s in self.serializers}
        querysets = self.get_queryset()

        return Response({
            (
                q.model.__name__.lower()
                .replace("profileavatar", "")
                .replace("clothes", "cloth")
                + "_form"
            ): c2s[q.model](q, context={"request": requests}, many=True).data
            for q in querysets
        })
