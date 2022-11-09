from copy import deepcopy
from typing import Any

from django.db import transaction
from rest_framework import viewsets, mixins, permissions, status, decorators, views
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Profile, ProfileAvatarFace, ProfileAvatarBrows
from accounts.serializers import (
    ProfileSerializer,
    ProfileStatisticsSerializer,
    ProfileStatisticsUpdateSerializer,
    ProfileHairSerializer,
    ProfileFaceSerializer,
    ProfileHeadSerializer,
    ProfileBrowsSerializer,
    ProfileClothesSerializer
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
        return self.request.user.profile.get(course_id=1)

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
        profile_statistics = request.user.profile.get(course_id=1).statistics
        serializer: ProfileStatisticsSerializer = self.get_serializer(instance=profile_statistics)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[NegativeResourcesException]
    ))
    @decorators.action(methods=["PATCH"], detail=False, url_path="statistics/update")
    def update_statistics(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile_statistics = request.user.profile.get(course_id=1).statistics
        serializer: ProfileStatisticsUpdateSerializer = self.get_serializer(
            instance=profile_statistics,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class AvatarViewSet(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    serializers = [
        ProfileHairSerializer,
        ProfileHeadSerializer,
        ProfileClothesSerializer
    ]

    def get_queryset(self):
        return [
            s.Meta.model.objects.all()
            for s in self.serializers
        ]

    def _filter_by_gender(self, data: dict, gender: str) -> dict:
        for key, values in data.items():
            data[key] = list(filter(lambda x: x["gender"] == gender, values))

        return data

    def list(self, request, *args, **kwargs):
        c2s = {s.Meta.model: s for s in self.serializers}
        querysets = self.get_queryset()

        parts_data = {
            (
                q.model.__name__.lower()
                .replace("profileavatar", "")
                .replace("clothes", "cloth")
                + "_form"
            ): c2s[q.model](q, context={"request": request}, many=True).data
            for q in querysets
        }
        parts_data["face_form"] = []

        for face_data in ProfileFaceSerializer(ProfileAvatarFace.objects.all(), many=True).data:
            for brows_data in ProfileBrowsSerializer(ProfileAvatarBrows.objects.all(), many=True).data:
                face_data = deepcopy(face_data)
                if brows_data["gender"] == face_data["gender"]:
                    face_data["brows"] = brows_data
                    parts_data["face_form"].append(face_data)

        # if request.user:
        #     parts_data = self._filter_by_gender(parts_data, request.user.profile.get().gender)

        return Response(parts_data)


class ReplayAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user

        profile = user.profile.get()

        with transaction.atomic():
            profile.user = None
            user.create_related_profile()
            profile.save()

        profile = user.profile.get()

        return Response(ProfileSerializer(profile).data)
