from rest_framework import viewsets, decorators, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from accounts.permissions import HasProfilePermission
from resources.models import Resources
from resources.serializers import ResourcesSerializer, ResourcesUpdateSerializer
from resources.exceptions import ResourcesNotFoundException
from resources.utils import get_max_energy_by_position


class ResourcesViewSet(viewsets.GenericViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    permission_classes = (IsAuthenticated, HasProfilePermission)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ResourcesUpdateSerializer
        return ResourcesSerializer

    @swagger_auto_schema(method="GET", responses={status.HTTP_200_OK: ResourcesSerializer()})
    @decorators.action(methods=["GET"], detail=False, url_path="retrieve")
    def retrieve_resources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
            Возвращаем ресурс, если он был.
            Если нет, создаем дефолтный ресурс для пользователя
        """
        profile = request.user.profile.first()
        user_resources, is_created = Resources.objects.get_or_create(user=profile)
        max_energy = get_max_energy_by_position(profile.university_position)

        if is_created:  user_resources.energy_amount = max_energy
        user_resources.energy_amount = min(user_resources.energy_amount, max_energy)
        user_resources.save()

        serializer: ResourcesSerializer = self.get_serializer_class()(instance=user_resources)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method="PATCH", responses={status.HTTP_200_OK: ResourcesSerializer()})
    @decorators.action(methods=["PATCH"], detail=False, url_path="update")
    def update_resources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = request.user.profile.first()
        user_resources = Resources.objects.filter(user=profile)
        if not user_resources.exists():
            raise ResourcesNotFoundException("Your profile doesn't have any resources")

        serializer: ResourcesUpdateSerializer = self.get_serializer_class()(
            data=request.data,
            instance=user_resources.first()
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serialized_data = ResourcesSerializer(instance=instance).data
        return Response(data=serialized_data, status=status.HTTP_200_OK)
