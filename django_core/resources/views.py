from rest_framework import viewsets, mixins, permissions, authentication, decorators, response, validators
from resources.models import Resources
from resources.serializers import ResourcesSerializer


class ResourceViewSet(viewsets.GenericViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer

    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (authentication.TokenAuthentication, )

    @decorators.action(methods=["GET"], detail=False, url_path='')
    def retrieve_resources(self, request, *args, **kwargs):
        """ Возвращаем ресурс, если он был, если нет, создаем дефолтный ресурс для пользователя """
        resource, _ = Resources.objects.get_or_create(user=request.user)
        return response.Response(ResourcesSerializer(resource).data)

    def validate_resource(self, resource):
        check_fields = ['time_amount', 'energy_amount', 'money_amount']
        errors = []

        for field in check_fields:
            if getattr(resource, field) < 0:
                errors.append(field)

        if errors:
            raise validators.ValidationError({field: "Negative value" for field in errors})

    @decorators.action(methods=["PATCH"], detail=False, url_path='update')
    def update_resources(self, request, *args, **kwargs):
        """ Нужно передать следующие данные:
        - timeDelta
        - energyDelta
        - moneyDelta

        Если какое нибудь из этих данных не будет предоставлено, то будет считаться, что изменений нет.
        """
        user_resources, _ = Resources.objects.get_or_create(user=request.user)

        time_delta = int(request.data.get('timeDelta', 0))
        energy_delta = int(request.data.get('energyDelta', 0))
        money_delta = int(request.data.get('moneyDelta', 0))

        if time_delta < 0:
            raise validators.ValidationError({"timeDelta": "Time is not suppose to be decreased"})

        user_resources.time_amount += time_delta
        user_resources.energy_amount += energy_delta
        user_resources.money_amount += money_delta

        self.validate_resource(user_resources)

        user_resources.save()

        return response.Response(ResourcesSerializer(user_resources).data)
