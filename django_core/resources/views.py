from rest_framework import viewsets, permissions, decorators, status
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from accounts.models import Profile
from resources.models import Resources
from resources.serializers import ResourcesSerializer, ResourcesUpdateSerializer
from resources.utils import profile_provided
from resources.exceptions import NegativeResourcesException


class ResourceViewSet(viewsets.GenericViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer

    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "PATCH":
            return ResourcesUpdateSerializer(*args, **kwargs)
        return ResourcesSerializer(*args, **kwargs)

    @swagger_auto_schema(method="GET", responses={status.HTTP_200_OK: ResourcesSerializer()})
    @decorators.action(methods=["GET"], detail=False, url_path="retrieve")
    @profile_provided
    def retrieve_resources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
            Возвращаем ресурс, если он был,
            если нет, создаем дефолтный ресурс для пользователя
        """
        profile = Profile.objects.filter(user=request.user).first()
        resource, _ = Resources.objects.get_or_create(user=profile)
        serializer: ResourcesUpdateSerializer = self.get_serializer_class(instance=resource)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method="PATCH", responses={status.HTTP_200_OK: ResourcesSerializer()})
    @decorators.action(methods=["PATCH"], detail=False, url_path="update")
    @profile_provided
    def update_resources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = Profile.objects.filter(user=request.user).first()
        user_resources, _ = Resources.objects.get_or_create(user=profile)

        serializer: ResourcesUpdateSerializer = self.get_serializer_class(data=request.data, instance=user_resources)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serialized_data = ResourcesSerializer(instance=instance).data

        return Response(data=serialized_data, status=status.HTTP_200_OK)
