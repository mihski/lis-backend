from rest_framework import viewsets, decorators, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings

from resources.exceptions import (
    NegativeResourcesException,
    UltimateAlreadyActivatedException
)
from resources.models import Resources
from resources.serializers import ResourcesSerializer, ResourcesUpdateSerializer
from resources.tasks import deactivate_ultimate
from resources.utils import (
    check_ultimate_is_active,
    get_ultimate_finish_dt
)


class ResourcesViewSet(viewsets.GenericViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    permission_classes = (IsAuthenticated,)

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
        serializer: ResourcesSerializer = self.get_serializer_class()(instance=profile.resources)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method="PATCH", responses={status.HTTP_200_OK: ResourcesSerializer()})
    @decorators.action(methods=["PATCH"], detail=False, url_path="update")
    def update_resources(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = request.user.profile.first()

        serializer: ResourcesUpdateSerializer = self.get_serializer_class()(
            data=request.data,
            instance=profile.resources
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serialized_data = ResourcesSerializer(instance=instance).data
        return Response(data=serialized_data, status=status.HTTP_200_OK)

    @decorators.action(methods=["POST"], detail=False, url_path="ultimate/activate")
    def activate_ultimate(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        profile = request.user.profile.first()
        resources = profile.resources

        if check_ultimate_is_active(profile):
            raise UltimateAlreadyActivatedException("You have already activated ultimate")

        if (remains := resources.money_amount - settings.ULTIMATE_COST) < 0:
            raise NegativeResourcesException("You don't have enough money to activate ultimate")

        resources.money_amount = remains
        resources.save()

        profile.ultimate_activated = True
        profile.ultimate_finish_datetime = get_ultimate_finish_dt(settings.ULTIMATE_DURATION)
        profile.save()

        deactivate_ultimate.apply_async(args=[profile.id], countdown=settings.ULTIMATE_DURATION)
        return Response(ResourcesSerializer(resources).data)
