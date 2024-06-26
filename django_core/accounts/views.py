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
    ProfileClothesSerializer,
    ProfileAlbumSerializer
)


from lessons.models import Course
from lessons.exceptions import NPCIsNotScientificDirectorException, FirstScientificDirectorIsNotDefaultException
from resources.exceptions import NegativeResourcesException
from helpers.swagger_factory import SwaggerFactory
from lessons.serializers import CourseNameSerializer

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
        "scientific_director",
        "user",
        "resources",
        "course",
    ).all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[NegativeResourcesException]
    ))
    @decorators.action(methods=["GET"], detail=False, url_path="profile/courses")
    def get_cources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
       
        return Response( status=status.HTTP_200_OK)

    def get_object(self):
        return self.request.user.profile.get(course_id=1)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[
            NPCIsNotScientificDirectorException,
            FirstScientificDirectorIsNotDefaultException
        ]
    ))
    def update(self, request, *args, **kwargs) -> Response:
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(**SwaggerFactory()(
        responses=[
            NPCIsNotScientificDirectorException,
            FirstScientificDirectorIsNotDefaultException
        ]
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

        faces_data = ProfileFaceSerializer(ProfileAvatarFace.objects.all(), context={"request": request}, many=True).data
        brows_datas = ProfileBrowsSerializer(ProfileAvatarBrows.objects.all(), context={"request": request}, many=True).data

        for face_data in faces_data:
            for brows_data in brows_datas:
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
        profile = user.profile.get(course_id=1)
        with transaction.atomic():
            profile.user = None
            user.create_related_profile()
            profile.save()
        profile = user.profile.get(course_id=1)
        return Response(ProfileSerializer(profile).data)


class ProfileAlbumViewSet(viewsets.GenericViewSet):
    queryset = Profile.objects.select_related("statistics", "emotions").all()
    serializer_class = ProfileAlbumSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @decorators.action(methods=["GET"], detail=False, url_path="album")
    def get_profile_album(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = request.user.profile.get(course_id=1)
        serialized_data = self.get_serializer(profile).data
        serialized_data["statistics"]["lessons_done"] = 36  # FIXME: hardcode
        return Response(serialized_data, status=status.HTTP_200_OK)


class ProfileCourseListApiView(views.APIView):
     def get(self, request):
         profile = request.user.profile.get()
         course = profile.course
         return Response(CourseNameSerializer(course).data)
     
     
     


